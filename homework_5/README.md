# Python Developer - Homework #5

## Web-server

Простой веб-сервер на Python для раздачи статичного контента.

Сервер построен на асинхронной архитектуре (asyncore_epoll) - файл httpd.py
Для примера приведена реализация того же сервера в неасинхронном варианте - файл httpd_noasync.py.
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
    Time taken for tests:   108.129 seconds
    Complete requests:      50000
    Failed requests:        78
       (Connect: 0, Receive: 39, Length: 0, Exceptions: 39)
    Write errors:           0
    Non-2xx responses:      49961
    Total transferred:      7693994 bytes
    HTML transferred:       0 bytes
    Requests per second:    462.41 [#/sec] (mean)
    Time per request:       216.259 [ms] (mean)
    Time per request:       2.163 [ms] (mean, across all concurrent requests)
    Transfer rate:          69.49 [Kbytes/sec] received

    Connection Times (ms)
                  min  mean[+/-sd] median   max
    Connect:        0   48 243.0      0    7246
    Processing:     0   97 3002.3      7  107104
    Waiting:        0   12 274.4      6   26727
    Total:          1  145 3040.6      8  108120

    Percentage of the requests served within a certain time (ms)
      50%      8
      66%     10
      75%     11
      80%     13
      90%     17
      95%     25
      98%   1031
      99%   1040
     100%  108120 (longest request)


Результаты тестирования неасинхронного сервера (в контейнере Docker)

    Server Software:        simple-http-server
    Server Hostname:        localhost
    Server Port:            8080

    Document Path:          /
    Document Length:        0 bytes

    Concurrency Level:      100
    Time taken for tests:   109.106 seconds
    Complete requests:      50000
    Failed requests:        68
       (Connect: 0, Receive: 34, Length: 0, Exceptions: 34)
    Write errors:           0
    Non-2xx responses:      49966
    Total transferred:      7694764 bytes
    HTML transferred:       0 bytes
    Requests per second:    458.27 [#/sec] (mean)
    Time per request:       218.213 [ms] (mean)
    Time per request:       2.182 [ms] (mean, across all concurrent requests)
    Transfer rate:          68.87 [Kbytes/sec] received

    Connection Times (ms)
                  min  mean[+/-sd] median   max
    Connect:        0   43 214.0      0    7201
    Processing:     0   89 2832.7      8  108095
    Waiting:        0   14 293.6      7   26702
    Total:          1  132 2867.7      9  109101

    Percentage of the requests served within a certain time (ms)
      50%      9
      66%     12
      75%     13
      80%     15
      90%     19
      95%     26
      98%   1032
      99%   1041
     100%  109101 (longest request)


