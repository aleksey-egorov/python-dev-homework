# Python Developer - Homework #5

## Web-server

Простой веб-сервер на Python для раздачи статичного контента.

Сервер построен на forking архитектуре - основной процесс запускает несколько дочерних процессов (по кол-ву воркеров),
которые обрабатывают входящие запросы.

Ниже приводятся результаты нагрузочного тестирования обоих серверов.

Параметры запуска:
* port - порт сервера (по умолчанию 8080)
* log - файл логов (по умолчанию лог пишется в STDOUT)
* worker - количество воркеров (по умолчанию 1)
* root - папка с контентом (по умолчанию /htdocs)

Используется Python 3.6

### Примеры запуска

Запуск сервера на порту 8080 с 10 воркерами и файлом логов:

    python3.6 httpd.py --port=8080 --worker=10 --root=./htdocs/ --log=httpd.log

Запуск unit-тестирования:

    python3.6 httptest.py

Запуск нагрузочного тестирования

    sh test.sh

### Нагрузочное тестирование

Результаты тестирования асинхронного сервера (в контейнере Docker)

    Server Software:        simple-http-server
    Server Hostname:        localhost
    Server Port:            8080

    Document Path:          /
    Document Length:        0 bytes

    Concurrency Level:      100
    Time taken for tests:   107.252 seconds
    Complete requests:      50000
    Failed requests:        70
       (Connect: 0, Receive: 35, Length: 0, Exceptions: 35)
    Write errors:           0
    Non-2xx responses:      49965
    Total transferred:      7694610 bytes
    HTML transferred:       0 bytes
    Requests per second:    466.19 [#/sec] (mean)
    Time per request:       214.504 [ms] (mean)
    Time per request:       2.145 [ms] (mean, across all concurrent requests)
    Transfer rate:          70.06 [Kbytes/sec] received

    Connection Times (ms)
                  min  mean[+/-sd] median   max
    Connect:        0   29 176.0      0    3041
    Processing:     0   84 2822.9      4  106238
    Waiting:        0    9 274.0      3   26636
    Total:          1  113 2855.6      5  107247

    Percentage of the requests served within a certain time (ms)
      50%      5
      66%      6
      75%      7
      80%      8
      90%     11
      95%     14
      98%   1018
      99%   1030
     100%  107247 (longest request)



