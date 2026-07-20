from django.db import models


class EventCategory(models.Model):
    name = models.CharField(max_length=255)
    criterion = models.ForeignKey(
        "stsv_app.TrainingCriterion", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ duyệt"
        APPROVED = "APPROVED", "Đã duyệt"
        REJECTED = "REJECTED", "Từ chối"

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    organizer = models.ForeignKey(
        "stsv_app.User", on_delete=models.CASCADE, related_name="organized_events"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    target_audiences = models.JSONField(blank=True, null=True)
    max_participants = models.IntegerField()
    waiting_list_capacity = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    approved_by = models.ForeignKey(
        "stsv_app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_events",
    )
    is_youth_union = models.BooleanField(default=False)
    training_points = models.IntegerField(default=0)
    app_route = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


class CheckInSession(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    dynamic_code = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Đã đăng ký"
        WAITLIST = "WAITLIST", "Danh sách chờ"
        CANCELLED = "CANCELLED", "Đã hủy"

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REGISTERED
    )
    queue_position = models.IntegerField(default=0)
    is_checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    feedback_submitted = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)


class YouthUnionRecord(models.Model):
    class SyncStatus(models.TextChoices):
        SYNCED = "SYNCED", "Đã đồng bộ"
        PENDING_SYNC = "PENDING_SYNC", "Chờ đồng bộ"
        FAILED = "FAILED", "Thất bại"

    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    sync_status = models.CharField(
        max_length=20, choices=SyncStatus.choices, default=SyncStatus.PENDING_SYNC
    )
    sync_response = models.TextField(blank=True)
