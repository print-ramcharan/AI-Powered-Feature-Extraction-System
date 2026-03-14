# Strategy: Incremental & Partitioned Training

## Objective
To enable training on massive datasets (70k+ images) using time-limited cloud environments (Kaggle 12hr limit, Colab 8hr-12hr limit) by training on sequential data partitions.

## Technical Approach
Instead of one massive training loop, the team will use **Checkpointed fine-tuning**.

### The Workflow:
1.  **Partition 1:** Initial training on `chhattisgarh_vol1`.
    *   Command: `model.train(data='vol1.yaml', epochs=10, save=True)`
    *   Output: `runs/train/weights/last.pt`
2.  **Partition 2:** Load the weights from the previous run.
    *   Command: `model = YOLO('runs/train/weights/last.pt')`
    *   Command: `model.train(data='vol2.yaml', epochs=10)`
    *   This "continues" the learning on a new dataset slice.
3.  **Repeat:** Iterate through all 24 individual Kaggle volumes (`chhattisgarh-vol1` through `chhattisgarh-vol24`).

## Benefits
-   **No Timeouts:** You can stop after any volume and save the weights.
    -   **Checkpoint Reliability:** If a browser closes or a notebook restarts, you only lose progress on the *current* volume, not the whole project. Since each volume is its own Kaggle dataset, downloading is faster and more granular.
    -   **Memory Efficiency:** The GPU only has to cache a smaller subset of images at a time.
    -   **Validation Snapshots:** We can evaluate metrics (`mAP50`) after every volume to see if the model is actually getting smarter or if it's "forgetting" old data (Catastrophic Forgetting).

## Risk Mitigation: Catastrophic Forgetting
When training on new volumes, the model might "forget" features from the first volume. 
**Fix:** Every 5th partition, we will include a "Review Set" (a small 5% random sample of images from ALL previous volumes) to keep the old features fresh in the model's memory.

---
*Status: Research Phase - Proposed by Ram*
