import numpy as np
import matplotlib.pyplot as plt
import colorsys

def create_RGB_list(N):
    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    return RGB_tuples

def line_type(line):
    if 0 == line.count('/'):
        return 'header'
    if 1 == line.count('/'):
        return 'header'
    if 2 == line.count('/'):
        return 'clicks'
    if 3 == line.count('/'):
        return 'course'
    if 4 == line.count('/'):
        return 'exam'
    if 5 == line.count('/'):
        return 'question'
    return 'other'

def hms_to_sec(mytime):
    h,m,s = mytime.split(':')
    return int(s) + 60*int(m) + 60*60*int(h)

def add_to_target_dict(line,target_dict):
    page,pageviews,unique_pageviews,unique_visitors,avg_time,pages_per_visit,visit_duration = line.strip().split(',')
    target_dict['pageviews'] = int(pageviews)
    target_dict['unique_pageviews'] = int(unique_pageviews)
    target_dict['avg_time'] = hms_to_sec(avg_time)
    target_dict['pages_per_visit'] = float(pages_per_visit)
    target_dict['visit_duration'] = hms_to_sec(visit_duration)
    return target_dict

def add_course_info(page_info,line,course_name):
    if not page_info.has_key(course_name):
        page_info[course_name] = {}
    target_dict = page_info[course_name]
    target_dict = add_to_target_dict(line,target_dict)
    return page_info

def add_exam_info(page_info,line,course_name,exam_name):
    if not page_info.has_key(course_name):
        page_info[course_name] = {}
    if not page_info[course_name].has_key(exam_name):
        page_info[course_name][exam_name] = {}
    target_dict = page_info[course_name][exam_name]
    add_to_target_dict(line,target_dict)
    return page_info

def add_question_info(page_info,line,course_name,exam_name,question_name):
    if not page_info.has_key(course_name):
        page_info[course_name] = {}
    if not page_info[course_name].has_key(exam_name):
        page_info[course_name][exam_name] = {}
    page_info[course_name][exam_name][question_name] = {}
    target_dict = page_info[course_name][exam_name][question_name]
    add_to_target_dict(line,target_dict)
    return page_info

def add_page_info(page_info,line,which_type):
    if 'exam' == which_type:
        course_name = line.split(',')[0].split('/')[-2]
        exam_name = line.split(',')[0].split('/')[-1]
        page_info = add_exam_info(page_info,line,course_name,exam_name)
    elif 'course' == which_type:
        course_name = line.split(',')[0].split('/')[-1]
        page_info = add_course_info(page_info,line,course_name)
    elif 'question' == which_type:
        course_name = line.split(',')[0].split('/')[-3]
        exam_name = line.split(',')[0].split('/')[-2]
        question_name = line.split(',')[0].split('/')[-1]
        page_info = add_question_info(page_info, line, course_name, exam_name, question_name)
    return page_info

def list_courses(page_info):
    sorted_keys = sorted(page_info.keys())
    list_of_courses = []
    for key in sorted_keys:
        if type({}) == type(page_info[key]):
            list_of_courses.append(key)
    return list_of_courses

def list_exams(page_info, course):
    list_of_exams = []
    sorted_keys = sorted(page_info[course].keys())
    for key in sorted_keys:
        if type({}) == type(page_info[course][key]):
            list_of_exams.append(key)
    return list_of_exams

def list_questions(page_info, course, exam):
    list_of_questions = []
    sorted_keys = sorted(page_info[course][exam].keys())
    for key in sorted_keys:
        if type({}) == type(page_info[course][exam][key]):
            list_of_questions.append(key)
    return list_of_questions

def print_course_exam_questions(page_info):
    for course in list_courses(page_info):
        for exam in list_exams(page_info,course):
            print course,exam,list_questions(page_info,course,exam)

def visit_duration_dist(page_info, course, include_subpages=True):
    front_page_dist = {}
    front_and_subpages_dist = {}
    for exam in list_exams(page_info, course):
        try:
            front_page_dist[exam] = page_info[course][exam]['visit_duration']
            front_and_subpages_dist[exam] = front_page_dist[exam]
            for question in list_questions(page_info, course, exam):
                front_and_subpages_dist[exam] += page_info[course][exam][question]['visit_duration']
        except ValueError:
            continue
    if not include_subpages:
        return front_page_dist
    else:
        return front_and_subpages_dist

def plot_visit_duration_dist(page_info, course, style='pie', include_subpages=True):
    dict_to_plot = visit_duration_dist(page_info, course, include_subpages)
    y = np.zeros(len(dict_to_plot.keys()))
    my_labels = []
    for num,key in enumerate(sorted(dict_to_plot.keys())):
        y[num] = dict_to_plot[key]
        if 'pie' == style:
            my_labels.append(key.replace('_','') + ' [' + str(int(y[num]/60/60)) + 'h ' + str(int(100*round(float(dict_to_plot[key])/sum(dict_to_plot.values()),2))) + '%]')
        elif 'bar' == style:
            my_labels.append(key.replace('December_','Dec').replace('April_','Apr') + '\n' + str(int(100*round(float(dict_to_plot[key])/sum(dict_to_plot.values()),2))) + '%')
    if 'pie' == style:
        plt.pie(y, labels = my_labels, startangle = 90)
    elif 'bar' == style:
        plt.bar(range(len(y)),y/60/60,align='center',color=create_RGB_list(len(y)))
        plt.gca().set_xticks(range(len(y)))
        plt.gca().set_xticklabels(my_labels)
        plt.ylabel('Total pageview time in hours')
    plt.title(course + ' - Total pageview time per exam')

def data_to_info_clicks(filename):
    f = open(filename,'r')
    page_info = {}
    clicks_time_series = []
    for line in f:
        if line_type(line) == 'header':
            continue
        elif line_type(line) == 'exam' or line_type(line) == 'course' or line_type(line) == 'question':
            page_info = add_page_info(page_info,line,line_type(line))
        elif line_type(line) == 'clicks':
            clicks_time_series.append(int(line.split(',')[1].strip()))
    return page_info,clicks_time_series

def plot_clicks(num_clicks):
    myarray = np.asarray(num_clicks)
    plt.plot(myarray)
    plt.xlabel('Days since start of term')
    plt.ylabel('Number of clicks')
    plt.title('Total number of clicks: ' + str(np.sum(myarray)))
