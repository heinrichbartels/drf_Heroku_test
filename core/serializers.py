from rest_framework import serializers
from .models import (Customer, Profession, Document, DataSheet)


class DataSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSheet
        fields = ('id', 'description', 'historical_data')


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'description', 'status')


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'dtype', 'doc_number', 'customer')


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'dtype', 'doc_number', 'customer')
        read_only_fields = ('customer', )


class CustomerSerializer(serializers.ModelSerializer):
    num_professions = serializers.SerializerMethodField()
    # data_sheet = serializers.StringRelatedField()
    # data_sheet = serializers.PrimaryKeyRelatedField(read_only=True)
    data_sheet = DataSheetSerializer()
    # professions = serializers.StringRelatedField(many=True)
    professions = ProfessionSerializer(many=True)
    document_set = DocumentSerializer(many=True)

    class Meta:
        model = Customer
        fields = ('id', 'name', 'address', 'professions',
                  'data_sheet', 'active', 'status_message',
                  'num_professions', 'document_set')

    def get_num_professions(self, obj):
        return obj.num_professions()  # Uses method from models.py

    def get_data_sheet(self, obj):
        return obj.data_sheet.description

    def create(self, validated_data):
        # import pdb        # Imports python debugger allowing for debug actions to be set.
        # pdb.set_trace()   # Sets a break in the django execution allowing to debug code
        professions = validated_data.pop('professions')
        document_set = validated_data.pop('document_set')
        data_sheet = validated_data.pop('data_sheet')

        customer = Customer.objects.create(**validated_data)

        d_sheet = DataSheet.objects.create(**data_sheet)

        customer.data_sheet = d_sheet

        for doc in document_set:
            Document.objects.create(
                dtype=doc['dtype'],
                doc_number=doc['doc_number'],
                customer_id=customer.id
            )

        for profession in professions:
            prof = Profession.objects.create(**profession)
            customer.professions.add(prof)

        customer.save()

        return customer




