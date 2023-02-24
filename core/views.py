from django.shortcuts import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter   # Imports search filter functionality
from django.http.response import HttpResponseNotFound
from .models import Customer, Profession, Document, DataSheet
from .serializers import CustomerSerializer, ProfessionSerializer, DocumentSerializer, DataSheetSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly, DjangoModelPermissions


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', ]
    search_fields = ['=name', 'address', 'data_sheet__description']
    # ordering_fields = '__all__'
    ordering_fields = ['id', 'name', 'datasheet__description' ]
    ordering = ('-id')
    lookup_field = 'document'
    authentication_classes = [TokenAuthentication, ]

    def get_queryset(self):
        # import pdb        # Imports python debugger allowing for debug actions to be set.
        # pdb.set_trace()   # Sets a break in the django execution allowing to debug code
        address = self.request.query_params.get('address', None)
        cust_status = self.request.query_params.get('active', True)

        if address:
            customers = Customer.objects.filter(address__icontains=address, active=cust_status)
        else:
            customers = Customer.objects.filter(active=cust_status)

        return customers

    # def list(self, request, *args, **kwargs):
    #     customers = self.get_queryset()
    #     serializer = CustomerSerializer(customers, many=True)
    #     return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()   # alternately use Customer.objects.get(pk=kwargs['pk'])
        serializer = CustomerSerializer(obj)
        return Response(serializer.data)
        # return HttpResponseNotFound("Error 404 - Not Allowed to download this item")

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     # print(f"Name: {data['name']}")
    #     # print(f"Address: {data['address']}")
    #     # print(f"Data keys available: {dir(data)}")
    #     customer = Customer.objects.create(
    #         name=data['name'], address=data['address'], data_sheet_id=data['data_sheet']
    #     )
    #     profession = Profession.objects.get(id=data['profession'])
    #     customer.professions.add(profession)
    #     customer.save()
    #
    #     serializer = CustomerSerializer(customer)
    #     return Response(serializer.data)

    @action(detail=True)
    def deactivate(self, request, **kwargs):
        customer = self.get_object()
        customer.active = False
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    @action(detail=False)
    def deactivate_all(self, request, **kwargs):
        customers = self.get_queryset()
        customers.update(active=False)

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def activate(self, request, **kwargs):
        customer = self.get_object()
        customer.active = True
        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    @action(detail=False)
    def activate_all(self, request, **kwargs):
        customers = self.get_queryset()
        customers.update(active=True)

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def change_status(self, request, **kwargs):
        customers = self.get_queryset()
        customers.update(active=request.data['active'])

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = request.data
        customer = self.get_object()

        customer.name = data['name']
        customer.address = data['address']
        customer.data_sheet_id = data['data_sheet']

        for profession in customer.professions.all():
            customer.professions.remove(profession)

        profession = Profession.objects.get(id=data['profession'])
        customer.professions.add(profession)
        customer.save()

    def partial_update(self, request, *args, **kwargs):
        customer = self.get_object()
        customer.name = request.data.get("name", customer.name) # If "name" does not exist use customer.name
        customer.address = request.data.get("address", customer.address)
        customer.data_sheet_id = request.data.get("data_sheet", customer.data_sheet_id)

        new_profession = request.data.get('profession', "")  # Only change profession if new_profession != ""

        if new_profession != "":
            for profession in customer.professions.all():
                customer.professions.remove(profession)
            customer.professions.add(new_profession)
        else:
            pass

        customer.save()

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        cust_id = customer.id
        name = customer.name
        customer.delete()

        return Response(data=f"Object {name} with id {cust_id} has been deleted", status=status.HTTP_204_NO_CONTENT)
        # Response(f"Object {name} with id {cust_id} has been deleted")


class ProfessionViewSet(viewsets.ModelViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAdminUser, ]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [DjangoModelPermissions, ]


class DataSheetViewSet(viewsets.ModelViewSet):
    queryset = DataSheet.objects.all()
    serializer_class = DataSheetSerializer
    permission_classes = [AllowAny, ]

