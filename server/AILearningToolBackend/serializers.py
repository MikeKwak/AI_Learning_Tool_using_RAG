from rest_framework import serializers

class PDFUploadSerializer(serializers.Serializer):
    documents = serializers.ListField(
        child=serializers.FileField()
    )

class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
