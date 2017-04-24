import shutil
from rest_framework.views import APIView
import subprocess
from rest_framework import status
import os
import re
from rest_framework.response import Response
import hashlib
from difflib import SequenceMatcher
import urllib2
import traceback

class FrontAutomate(APIView):

    def post(self, request):

        #constants
        html_second_error_bar = 10
        html_first_error_bar = 20
        css_error_bar = 4
        js_indent_bar = 80
        js_error_bar = 15

        try:
            git_url = "https://github.com/guptashubham101/samples"

            if git_url:
                end_name = str(git_url).split('/')[-1]
                project_folder = end_name + '-' + str(hashlib.sha1(os.urandom(128)).hexdigest())[:5]
                os.chdir('temp')
                points = 5
                html_list = []
                css_list = []
                js_list = []
                file_errors = 0
                number_of_lines = 0
                output = subprocess.call(['git', 'clone', git_url, project_folder])
                os.chdir(project_folder)
                path = os.getcwd()
                for folder in os.listdir(path):

                    if re.search('.html', folder):
                        html_list += [folder]
                    elif re.search('.css', folder):
                        css_list += [folder]
                    elif re.search('.js', folder):
                        js_list += [folder]
                    else:
                        pass

                    if os.path.isdir(folder):
                        for file in os.listdir(folder):

                            if os.path.isfile(folder + '/' + file):
                                if re.search('.html', file):
                                    html_list += [folder + '/' + file]
                                elif re.search('.css', file):
                                    css_list += [folder + '/' + file]
                                elif re.search('.js', file):
                                    js_list += [folder + '/' + file]
                                else:
                                    pass

                #Code quality check of html
                for html_file in html_list:
                    p = subprocess.Popen(["htmlhint", html_file], stdout=subprocess.PIPE)
                    error = p.communicate()
                    error = str(error)
                    found = re.search('files,(.*?)errors', error).group(0)
                    found = re.findall(r'\d+', found)
                    if found:
                        count = found[0]
                        file_errors += int(count)
                    else:
                        pass

                    html_file = open(html_file, 'r')
                    html_file = html_file.read()
                    lines = html_file.splitlines()
                    number_of_lines += len(lines)

                if number_of_lines:
                    ratio = (float(file_errors) / float(number_of_lines)) * 100
                    if ratio >= html_first_error_bar:
                        points -= 2

                    elif ratio >= html_second_error_bar:
                        points -= 1

                    else:
                        pass

                else:
                    points -= 2

                number_of_lines = 0
                counter = 0
                file_errors = 0

                # Code quality check of css
                for css_file in css_list:
                    p = subprocess.Popen(["csslint", css_file], stdout=subprocess.PIPE)
                    error = p.communicate()
                    error = str(error)
                    css_file = open(css_file, 'r')
                    css_file = css_file.read()
                    lines = css_file.splitlines()
                    number_of_lines += len(lines)
                    found = re.search('(.*?) in', error).group(0)
                    found = re.findall(r'\d+', found)
                    if found:
                        count = found[0]
                        file_errors += int(count)
                    else:
                        pass

                if number_of_lines:
                    ratio = (float(file_errors) / float(number_of_lines)) * 100
                    if ratio >= css_error_bar:
                        points -= 1

                else:
                    points -= 1

                number_of_lines = 0
                ratio_of_similarity = 0
                file_errors = 0

                # Code quality check of js
                for js_file in js_list:
                    counter += 1
                    p = subprocess.Popen(["jshint", js_file], stdout=subprocess.PIPE)
                    error = p.communicate()
                    error = str(error)
                    document = subprocess.check_output(['js-beautify', js_file])
                    js_file = open(js_file, 'r')
                    js_file = js_file.read()
                    lines = js_file.splitlines()
                    number_of_lines += len(lines)
                    ratio_of_similarity += (SequenceMatcher(None, document, js_file).ratio()) * 100
                    found = re.findall(r'\d+', error)

                    if found:
                        count = found[-1]
                        file_errors += int(count)
                    else:
                        pass

                if number_of_lines:
                    ratio = (float(file_errors)/float(number_of_lines)) * 100
                    if ratio >= js_error_bar:
                        points -= 1

                    ratio = ratio_of_similarity/counter
                    if ratio <= js_indent_bar:
                        points -= 1

                else:
                    points -= 2

                response = {
                    'result': True,
                    'message': 'Code Quality Done',
                    'points': points
                }

                os.chdir("..")
                shutil.rmtree(project_folder, ignore_errors=True)
                os.chdir("..")

                return Response(response)
            else:
                response = {
                    'result': False,
                    'message': 'No code url is provided'
                }

                return Response(response)

        except Exception as e:

            traceback_string = traceback.format_exc()
            print traceback_string
            print e.message
            path = os.getcwd()
            tokens = path.split('/')
            if tokens[-1] != 'project':
                os.chdir("..")
            path = os.getcwd()
            tokens = path.split('/')
            if tokens[-1] != 'project':
                os.chdir("..")

            response = {
                'message': 'An error occurred',
                'result': False,
                'exception': e.message
            }

            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
