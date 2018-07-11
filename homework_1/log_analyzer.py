#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import os
import gzip
import datetime
import re
import sys
import json
import ConfigParser
import logging
import argparse
from collections import namedtuple
from collections import defaultdict

# Конфиг по умолчанию
config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "FILE_PATTERN": 'nginx-access-ui.log',
    "SCRIPT_LOG": '',
    "PARSING_RATIO": 0.95
}

# Используемые custom типы данных
LastData = namedtuple('last', 'filename date')
StatsData = namedtuple('stats', 'data requests_total time_total')

# Шаблон парсинга строки
logpats = r'(\S+) (\S+)  (\S+) \[(.*?)\] "(.*?)" (\d+) (\d+) "(\S+)" "(.*?)" "(\S+)" "(\S+)" "(\S+)" ([\d.]+)'
logpat = re.compile(logpats)


def main(config):

    # Определяем файл с последней датой
    latest = get_latest_file(config["LOG_DIR"], config["FILE_PATTERN"])
    if latest.filename:

        # Готовим отчет
        log_path = os.path.join(config["LOG_DIR"], latest.filename)
        report_path = os.path.join(config["REPORT_DIR"], 'report-' + latest.date + '.html')
        if not os.path.exists(config["REPORT_DIR"]):
            os.makedirs(config["REPORT_DIR"])

        if not report_exists(report_path):
            logging.info("Processing path: " + log_path)

            # Собираем сводную информацию по всем запросам
            stats_data = prepare_stats(read_lines(log_path, config["PARSING_RATIO"]))

            # Расчитываем показатели и создаем финальный список для отчета
            report = make_final_list(stats_data, int(config["REPORT_SIZE"]))

            # Запись отчета в файл
            save_report(report, report_path)

    else:
        logging.error("No log file")


def get_latest_file(logdir, file_pattern):
    """Поиск файла с последней датой """

    latest_date = datetime.datetime.utcfromtimestamp(0)
    latest = LastData(filename=None, date=None)

    if os.path.exists(logdir):
        for file in os.listdir(logdir):

            # Обработка названия файла
            groups = re.match(r'^' + file_pattern + '-([\d]{8})([\.gz]?)', file)
            if groups:
                parts = groups.groups()
                date_str = parts[0]

                # Преобразуем дату из имени файла
                try:
                    tm = datetime.datetime.strptime(date_str, "%Y%m%d")
                except:
                    logging.exception("Date format is invalid")

                # Сохраняем имя файла с последней датой
                if tm > latest_date:
                    latest = LastData(filename=file, date=tm.strftime("%Y.%m.%d"))

    else:
        logging.error("Log directory doesn't exist")

    return latest


def report_exists(report_path):
    """Проверка существования отчета """

    if os.path.exists(report_path):
        logging.info("Report already exists ... exit")
        return True

    return False


def prepare_stats(lines):
    """Подготавливаем словарь с url запроса в виде ключа и списком request_time в виде значения"""

    stats = defaultdict(list)
    requests_total = 0
    time_total = 0.0

    for line in lines:
        req = line['request'].split(" ")

        if req[0] != '0':
            key = req[1]
            time = float(line['request_time'])
            stats[key].append(time)
            requests_total += 1
            time_total += time

    return StatsData(data=stats, requests_total=requests_total, time_total=time_total)


def make_final_list(stats, report_size):
    """Расчет показателей для отчета"""

    report = []
    for key in stats.data.keys():
        count = len(stats.data[key])
        count_perc = round(float(100 * float(count) / float(stats.requests_total)), 3)
        time_sum = round(sum(stats.data[key]), 3)
        time_avg = round(time_sum / count, 3)
        time_med = round(median(stats.data[key]), 3)
        time_max = round(max(stats.data[key]), 3)
        time_perc = round(float(100 * float(time_sum) / float(stats.time_total)), 3)
        report.append({
            'url': key,
            'count': count,
            'count_perc': count_perc,
            'time_sum': time_sum,
            'time_avg': time_avg,
            'time_med': time_med,
            'time_max': time_max,
            'time_perc': time_perc
        })

    # Сортируем данные по убыванию time_sum и обрезаем лишнее
    report.sort(key=lambda x: x['time_sum'], reverse=True)
    report = report[:report_size]

    return report


def save_report(report, report_path):
    """Запись отчета в файл"""

    try:
        with open('report.html', 'r') as tmpl:
            content = tmpl.read()
            content = content.replace('$table_json', json.dumps(report))
        with open(report_path + '.tmp', 'w') as rp_file:
            rp_file.write(content)
    except:
        logging.exception("Error writing report file")

    os.rename(report_path + '.tmp', report_path)
    logging.info("Report complete")
    return report_path


def median(lst):
    """Расчет медианы """

    n = len(lst)
    if n < 1:
        return 0.0
    if n % 2 == 1:
        return sorted(lst)[n//2]
    else:
        return sum(sorted(lst)[n//2-1:n//2+1])/2.0


def read_lines(log_path, parsing_ratio):
    """Чтение строк из файла """

    if log_path.endswith(".gz"):
        log = gzip.open(log_path,'rb')
    else:
        log = open(log_path)

    total = processed = 0
    for line in log:
        parsed_line = process_line(line)
        total += 1
        if parsed_line:
            processed += 1
            yield parsed_line

    # Проверка: если доля обработанных строк меньше parsing_ratio - ошибка формата данных
    if processed / total < parsing_ratio:
        raise RuntimeError("Too much parsing errors, check log file format")

    logging.info("%s of %s lines processed" % (processed, total))
    log.close()


def process_line(line):
    """Парсинг строки """

    try:
        groups = logpat.match(line)
        tuples = groups.groups()

        colnames = ('remote_addr', 'remote_user', 'http_x_real_ip', 'time_local', 'request', 'status', 'body_bytes_sent', 'http_referer', 'http_user_agent',
                    'http_x_forwarded_for', 'http_x_request_id', 'http_x_rb_user', 'request_time')

        log = dict(zip(colnames, tuples))
        return log

    except:
        return False


def init_log(filename):
    """Инициализация лога """

    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    logging.basicConfig(format=u'[%(asctime)s] %(levelname).1s %(message)s', datefmt=u'%Y.%m.%d %H:%M:%S',
                        level=logging.DEBUG, filename=filename)


def parse_config_file(config_file, config):
    """Обработка конфиг файла """

    if os.path.exists(config_file):
        conf = ConfigParser.ConfigParser()
        conf.read(config_file)

        props = ("REPORT_SIZE", "LOG_DIR", "REPORT_DIR", "FILE_PATTERN", "SCRIPT_LOG", "PARSING_RATIO")
        for prop in props:
            value = None

            # В config меняются только найденные значения из файла, остальное - без изменения.
            try:
                value = conf.get("Main", prop)
                if value:
                    config[prop] = value
            except:
                pass

    else:
        raise RuntimeError("Error in config file")

    return config


if __name__ == "__main__":

    # Обработка параметров скрипта
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="config file", default="./config/config.conf")
    args = parser.parse_args()
    config_file = args.config
    config = parse_config_file(config_file, config)

    # Инициализация лога и запуск скрипта
    init_log(config["SCRIPT_LOG"])
    logging.info("Starting analyzer ... ")
    logging.info("Config file parsing complete")

    try:
        main(config)
    except:
        logging.exception("Exception raised")
