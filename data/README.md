# Data used in these labs

`train.csv`, `baseline.csv` and `new_same_distribution.csv` come from the [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection).

Attribution: Almeida, T. and Hidalgo, J. (2011), *SMS Spam Collection*, UCI Machine Learning Repository, DOI [10.24432/C5CC84](https://doi.org/10.24432/C5CC84). UCI lists the dataset under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The archive README text is retained alongside the split files, converted to UTF-8 with LF line endings.

The preparation script removes duplicate message text before creating stratified splits with seed 42: about 70% training, 15% baseline evaluation and 15% a control evaluation set. It fits no text transformation during data preparation. `split_manifest.json` records the actual row counts and hashes. These are random splits of historical data, not chronological future samples.

`new_messages.csv` contains 40 synthetic examples written for this workshop: 20 spam scenarios and 20 ordinary messages. The spam labels assume the requests describe an impersonation or phishing attempt. This is a deliberately different teaching sample, not evidence of actual production drift. Its class balance differs from UCI. A small synthetic sample cannot establish a production retraining policy.

All CSV files have the columns `label,message`. Use `spam` or `ham` for labels. Use public or synthetic examples in the public repository. Do not upload students' private SMS messages.

To recreate the UCI splits after setup, run from the repository root:

```bash
python scripts/download_data.py
```

This command requires internet access and rewrites only the three UCI split files, their manifest and original README. The provided synthetic file stays separate.
