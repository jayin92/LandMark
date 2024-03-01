# The conversion scripts for Google Earth datasets from SGAM


import argparse
import json
import os
import numpy as np
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="convert colmap to transforms_train/test.json")

    parser.add_argument("--recon_dir", type=str, default="landmark/dataset/your_dataset/sparse/0")
    parser.add_argument("--output_dir", type=str, default="landmark/dataset/your_dataset")
    parser.add_argument("--holdout", type=int, default=50)

    args = parser.parse_args()
    return args


def ge_to_json(recon_dir, output_dir, holdout):

    with open(os.path.join(recon_dir, "transforms.json"), "rb") as f:
        transforms = json.load(f)

    extrinsics = {
        "w": 512,
        "h": 512,
        "k1": 0,
        "k2": 0,
        "p1": 0,
        "p2": 0,
    }

    extrinsics["fl_x"] = transforms["camera_intrinsics"][0][0]
    extrinsics["fl_y"] = transforms["camera_intrinsics"][1][1]
    extrinsics["cx"] = transforms["camera_intrinsics"][0][2]
    extrinsics["cy"] = transforms["camera_intrinsics"][1][2]

    frames = []
    # stats = np.zeros((100, 100))
    for frame in transforms["frames"]:
        if not frame['is_valid']:
            continue
        # stats[frame['grid_i'], frame['grid_j']] += 1
        # if frame['grid_i'] > 30 or frame['grid_j'] > 30:
        #     continue
        
        name = frame["file_path"].split("/")[-1]
        transforms_matrix = np.array(frame["transform_matrix"])
        transforms_matrix = transforms_matrix
        frame = {
            "file_path": name,
            "transform_matrix": transforms_matrix.tolist(),
            "grid_i": frame["grid_i"],
            "grid_j": frame["grid_j"],
        }
        frames.append(frame)
    # import ipdb
    # ipdb.set_trace()
    out_train = dict(extrinsics)
    out_test = dict(extrinsics)

    frames_train = [f for i, f in enumerate(frames) if i % holdout != 0 and i % 3 == 1]
    frames_test = [f for i, f in enumerate(frames) if i % holdout == 0]

    out_train["frames"] = frames_train
    out_test["frames"] = frames_test

    print("Train frames:", len(frames_train))
    print("Test frames:", len(frames_test))

    with open(output_dir / "transforms_train.json", "w", encoding="utf-8") as f:
        json.dump(out_train, f, indent=4)

    with open(output_dir / "transforms_test.json", "w", encoding="utf-8") as f:
        json.dump(out_test, f, indent=4)

    return len(frames)


if __name__ == "__main__":
    init_args = parse_args()
    Recondir = Path(init_args.recon_dir)
    Outputdir = Path(init_args.output_dir)
    Holdout = init_args.holdout
    ge_to_json(Recondir, Outputdir, Holdout)
