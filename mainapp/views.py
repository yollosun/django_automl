import os

from django.shortcuts import render, redirect

import pandas as pd
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
from .models import File, GraphData
from .serializers import FileSerializer, GraphDataSerializer
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
        print(file_details)
        columns = df.columns

        serializer = FileSerializer(data=file_details)
        if serializer.is_valid():
            serializer.save()
            return Response(columns, status=201)
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
        df = pd.read_csv(serializer.data[-1]["path"] + "\{file}".format(file=request.data['name']))

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

class CreateDateModel(APIView):
    def post(self, request, format=None):
        print("im here")
        name_of_file = request.data['name']
        id = request.user.id
        path_to_file = os.path.join(MEDIA_ROOT, str(id), name_of_file)
        print(path_to_file)

        target_variable = request.data['target_variable']
        resp = main_function(path_to_file, target_variable)
        # data = {
        #     'name': request.data['name'],
        #     'owner': id
        # }
        return Response([resp])



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


