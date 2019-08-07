from rest_framework import serializers

from core.models import Score


class ScoreSerializer(serializers.ModelSerializer):
    """Serializer for score object"""

    class Meta:
        model = Score
        fields = ('id', 'version', 'score_overall', 'score_medical',
                  'score_income', 'score_stuff', 'score_liability',
                  'score_digital', 'desc_overall', 'desc_medical',
                  'desc_income', 'desc_stuff', 'desc_liability',
                  'desc_digital')
        read_only_fields = ('id',)