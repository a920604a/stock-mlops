from prometheus_client import Counter, Histogram


train_success_total = Counter(
    "train_success_total", "Number of successful training jobs"
)
train_failure_total = Counter("train_failure_total", "Number of failed training jobs")

train_duration_seconds = Histogram(
    "train_duration_seconds", "Training duration in seconds"
)


predict_success_total = Counter(
    "predict_success_total", "Number of successful predict jobs"
)
predict_failure_total = Counter(
    "predict_failure_total", "Number of failed predict jobs"
)
predict_duration_seconds = Histogram(
    "predict_duration_seconds", "Predicting duration in seconds"
)
