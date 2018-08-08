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

Запуск тестирования:

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
Time taken for tests:   356.197 seconds
Complete requests:      50000
Failed requests:        204
   (Connect: 0, Receive: 102, Length: 0, Exceptions: 102)
Write errors:           0
Non-2xx responses:      49898
Total transferred:      7684292 bytes
HTML transferred:       0 bytes
Requests per second:    140.37 [#/sec] (mean)
Time per request:       712.394 [ms] (mean)
Time per request:       7.124 [ms] (mean, across all concurrent requests)
Transfer rate:          21.07 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0  153 577.2      0   15862
Processing:     0  284 4948.2     32  147895
Waiting:        0   58 571.9     27   53359
Total:          0  437 5029.4     34  148933

Percentage of the requests served within a certain time (ms)
  50%     34
  66%     40
  75%     46
  80%     51
  90%   1047
  95%   1104
  98%   1884
  99%   3320
 100%  148933 (longest request)


Результаты тестирования неасинхронного сервера (в контейнере Docker)

Server Software:        simple-http-server
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   260.556 seconds
Complete requests:      50000
Failed requests:        28
   (Connect: 0, Receive: 14, Length: 0, Exceptions: 14)
Write errors:           0
Non-2xx responses:      49986
Total transferred:      7697844 bytes
HTML transferred:       0 bytes
Requests per second:    191.90 [#/sec] (mean)
Time per request:       521.112 [ms] (mean)
Time per request:       5.211 [ms] (mean, across all concurrent requests)
Transfer rate:          28.85 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0  168 547.9      4   15372
Processing:    -2   93 1995.4     23  160432
Waiting:        0   57 445.7     18   53100
Total:          0  261 2108.9     30  161500

Percentage of the requests served within a certain time (ms)
  50%     30
  66%     40
  75%     48
  80%     56
  90%   1059
  95%   1136
  98%   1949
  99%   3200
 100%  161500 (longest request)

