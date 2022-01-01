import os

from django.shortcuts import render, redirect
import pickle
import pandas as pd

from django.shortcuts import HttpResponse
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import QueryDict, JsonResponse
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from autoML.settings import MEDIA_ROOT
from rest_framework import status
from pathlib import Path
from .models import File, GraphData, DataModel
from .serializers import FileSerializer, GraphDataSerializer, DataModelSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import ListView
import json
from .modellearn import *

class MyUploadView(APIView):
    parser_class = (FileUploadParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data
        id = request.user.id
        dir = os.path.join(MEDIA_ROOT, str(id))
        if not os.path.exists(dir):
            os.mkdir(dir)
        if Path(str(f['file'])).suffix[1:].lower() == 'xlsx':
            df = pd.read_excel(f['file'])
            file = df.to_csv(os.path.join(MEDIA_ROOT,str(id), "{name}.csv".format(name=str(f['file'])[:str(f['file']).find('.')])))
        else:
            df = pd.read_csv(f['file'])
            file = df.to_csv(os.path.join(MEDIA_ROOT, str(id), "{name}.csv".format(name=str(f['file'])[:str(f['file']).find('.')])))

        file_details = {
            'name': "{name}.csv".format(name=str(f['file'])[:str(f['file']).find('.')]),
            'owner': id,
            'path': dir,
            'published_date': timezone.now()
        }
        #
        # print(file_details)
        # columns = df.columns
        serializer = FileSerializer(data=file_details)
        if serializer.is_valid():
            serializer.save()
            # return Response(columns, status=201)
            return Response("File uploaded")
        return JsonResponse(serializer.errors, status=400)

    def get(self, request, format=None):
        files = File.objects.filter(owner=request.user.id)

        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)

class ShowFileColumns(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        files = File.objects.filter(owner=request.user.id, name=request.data['name'])
        serializer = FileSerializer(files, many=True)
        df = pd.read_csv(serializer.data[-1]["path"] + "\{file}".format(file=request.data['name']), nrows=1)

        return Response(df.columns)


class Graph(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'list.html'
    template_name = 'list2.html'
    def post(self, request, format=None):
        print(request)
        # file = request.data['name'][:request.data['name'].find('.')]
        files = File.objects.filter(owner=request.user.id, name=request.data['name'])
        serializer = FileSerializer(files, many=True)
        print(serializer.data[-1]['path'])
        df = pd.read_csv(serializer.data[-1]["path"] + "\{file}".format(file=request.data['name']))
        # df = pd.read_csv(serializer.data[-1]["path"]+"\{file}".format(file=serializer.data[-1]["name"]))
        # dashi(df, x=request.data["x"], y=request.data["y"], typeOfGraph=request.data["typeOfGraph"])
        new_df = df[[request.data['x'], request.data['y']]]
        new_df.rename(columns={request.data['x']: 'x', request.data['y']: 'y'}, inplace=True)
        new_df = new_df.to_dict('list')
        graph_type = request.data['type']
        if graph_type == "scatter":
            mode = 'lines+markers'
            new_df['mode'] = mode
            new_df['type'] = graph_type
        elif graph_type == "line":
            mode = 'lines'
            new_df['mode'] = mode
            new_df['type'] = "scatter"
        elif graph_type == "dot_plot":
            mode = 'markers'
            new_df['mode'] = mode
            new_df['type'] = "scatter"
        elif graph_type == "log_plot":
            new_df['type'] = "scatter"
        else:
            new_df['type'] = graph_type
        graph_details = {
                'type': graph_type,
                'owner': request.user.id,
                'data': str(new_df),
            }
        serializer = GraphDataSerializer(data=graph_details)
        if serializer.is_valid():
            serializer.save()
            return Response(graph_details, status=201)
        return JsonResponse(serializer.errors, status=400)

    def get(self, request):
        graph = GraphData.objects.filter(owner=request.user.id)
        graph = GraphData.objects.all()
        serializer = GraphDataSerializer(graph, many=True)
        data = serializer.data[-1]['data']
        data = [eval(data)]
        graph_type = serializer.data[-1]['type']

        return Response({'df': data, 'type': graph_type})
        # data = {'x': [1, 2, 3, 4],
        #         'y': [10, 15, 13, 17],
        #         'mode': 'markers',
        #         'type': 'scatter'}
        # graph_type = 'scatter'
        # # return Response({'data': serializer.data})
        # data =[ {'x': ['Apples', 'Oranges', 'Bananas'], 'y': [20,  14, 5],
        #         'type': 'bar'}]
        # graph_type = 'bar'
        # print(serializer.data[-1]['type'])
        # return Response({'df': data, 'type': graph_type, "data": serializer})

class GraphView(ListView):
    template_name = "list.html"
    model = File
    queryset = File.objects.all()

class CreateDataModel(APIView):
    def post(self, request, format=None):
        name_of_file = request.data['name']
        id = request.user.id
        path_to_file = os.path.join(MEDIA_ROOT, str(id), name_of_file)
        print(path_to_file)

        target_variable = request.data['target_variable']
        model, model_score = main_function(path_to_file, target_variable)
        dir = os.path.join(MEDIA_ROOT, str(id), "picklemodels")
        if not os.path.exists(dir):
            os.mkdir(dir)
        pkl_filename = os.path.join(MEDIA_ROOT, str(id),"picklemodels", f"{name_of_file[:len(name_of_file)-4]}_model.pkl")
        with open(pkl_filename, 'wb') as file:
            pickle.dump(model, file)

        data = {
            'name': f"{name_of_file[:len(name_of_file)-4]}_model.pkl",
            'owner': id,
            'path': os.path.join(MEDIA_ROOT, str(id),"picklemodels", f"{name_of_file[:len(name_of_file)-4]}_model.pkl"),
            'target_variable': request.data['target_variable']
        }
        serializer = DataModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"model_score": model_score})
        return JsonResponse(serializer.errors, status=400)
    def get(self, request):
        files = DataModel.objects.filter(owner=request.user.id)
        serializer = DataModelSerializer(files, many=True)
        return Response(serializer.data)

class ReturnModel(APIView):
    def post(self, request, format=None):
        files = DataModel.objects.filter(owner=request.user.id, name=request.data['name'])
        serializer = DataModelSerializer(files, many=True)
        path = serializer.data[-1]['path']
        print(path)
        with open(path, 'rb') as file:
            pickle_model = pickle.load(file)
        pickle_model = pickle_model[0]
        x = request.data['file']
        try:
            df = pd.read_csv(x)
        except:
            df = pd.read_excel(x)
        X_test = fill_nan(df, df)
        X_test = categorical_processing(df)
        print("hgyftdrftgyhjkl")
        Ypredict = pickle_model.predict(X_test)
        print("here")
        data = pd.Series(Ypredict)
        df[serializer.data[-1]['target_variable']] = data
        geeks_object = df.to_html()

        return HttpResponse(geeks_object)

# def dashi(df, x, y, typeOfGraph, list=0):
#     print("Первая проверка")
#     app = dash.Dash(__name__)
#     if typeOfGraph == "scatter":
#         fig = px.scatter(df, x=x, y=y)
#     elif typeOfGraph == "bar":
#         fig = px.bar(df, x=x, y=y, barmode="group")
#     elif typeOfGraph == "line":
#         fig = px.line(df, x=x, y=y)
#     elif typeOfGraph == "area":
#         fig = px.area(df, x=x, y=y)
#     elif typeOfGraph == "funnel":
#         fig = px.funnel(df, x=x, y=y)
#     elif typeOfGraph == "histogram":
#         fig = px.histogram(df, x=x, y=y)
#     elif typeOfGraph == "density_heatmap":
#         fig = px.density_heatmap(df, x=x, y=y)
#     app.layout = html.Div(children=[
#             html.H1(children='Hello Dash'),
#
#             dcc.Graph(
#                 id='example-graph',
#                 figure=fig
#             )
#         ])
#     print("вторая проверка")
#     app.run_server(debug=True)


