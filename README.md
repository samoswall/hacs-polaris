# hacs-polaris 
![all](https://github.com/samoswall/hass-polaris/blob/main/logo&icon.png)

## Polaris IQ Home devices integration to Home Assistant
## Интеграция Home Assistant для техники Polaris.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![](https://img.shields.io/github/watchers/samoswall/hacs-polaris.svg)
![](https://img.shields.io/github/stars/samoswall/hacs-polaris.svg)

[![Donate](https://img.shields.io/badge/donate-Yandex-red.svg)](https://yoomoney.ru/fundraise/b8GYBARCVRE.230309)

> [!WARNING]
> Устройство Polaris должно быть подключено к вашему mqtt брокеру! <br>
> Подключить к mqtt брокеру можно в приложении в настройках. Если такой настройки нет, значит у вас старая версия прошивки в устройстве.<br>
> Новую версию прошивки можно запросить в техподдержке Polaris через приложение.<br>
> Если по какой-то причине нет возможности обновить прошивку, то можно воспользоваться решением, опиcанным на 4pda, перенаправив трафик в роутере на дополнительный брокер mqtt.<br>

> [!WARNING]
> Выяснилось, что у некотых устройств установлены пробные (с этапа тестирования) версии прошивок, некоторые из них не доработаны и не публикуют тип устройства (топик polaris/XXXXXXXXXXXX/state/devtype где ХХХХХХХХХХХХ mac адрес вашего устройства).<br>
> Без типа невозможно понять, что это за устройство. Варианты решения проблемы:<br>
> Запросить новую прошивку (с публикацией devtype) или самостоятельно опубликовать в топик polaris/XXXXXXXXXXXX/state/devtype тип устройства - число (ID) с установленным статусом retain из таблицы ниже.<br>
> Обратите внимание - устройства одинаковые, а функции могут быть разные (наличие/отсутствие веса или ночника). После изменения (публикации) типа - надо удалить устройство в интеграции и создать заново.

> :information_source: **Добавлены**: <br>
:heavy_check_mark: Чайники <br>
:heavy_check_mark: Увлажнители <br>
:heavy_check_mark: Мультиварки <br>

> :information_source: **Как добавить новое устройство**: <br>
Создаем issues - Добавить ...  <br>
Обязательно указать type(ID) устройства и желательно развернутый mqtt топик для понимания, что добавлять. <br>

> :information_source: **Возможные проблемы**: <br>
В чайниках - может отсутствовать(быть лишним) сенсор веса и сенсор на базе. Так же может не работать Ночник (потому что в чайнике его нет)<br>
Проблема - есть одинаковые модели как с весом так и без, с ночником и без. Отличаются type(ID). <br>
Не стесняемся, создаем issues - отсутствует(лишний) сенсор ... type ... <br>
По другим предложениям (проблемам, логике работы, иконкам, переводам) пишем issues <br>

> :information_source: **Планы для доработок**: <br>
:heavy_check_mark: Добавить поддержку старых устройств (со старой структурой топика) <br>
:heavy_check_mark: Добавить сенсор ошибок <br>
:black_large_square: Добавить устройсто online/offline <br>
:black_large_square: Добавить кофемашины, пылесосы и т.д.<br>

Доступно обсуждение тут: [Telegram](https://t.me/polarishomeassistant)

<details>
  <summary>Инструкция по подключению устройства к MQTT на примере чайника.</summary>

  1. Зайти в устройство в приложении и нажать на значок шестерёнки, чтобы перейти в настройки
     
     <img src='https://github.com/user-attachments/assets/187fc45c-2705-4111-845b-68cd21d9ff2c' width='200' alt='app screen 1'>
       
     Проверить, есть ли в настройках пункт "Настройки MQTT".
          
     <img src='https://github.com/user-attachments/assets/3b300b9b-02f5-457c-8e69-a9406d235270' width='200' alt='app screen 2'>
          
     Если его нет, то запросить прошивку в поддержке.
     Прошивка устанавливается долгим нажатием на строку с версией прошивки (не MCU).
  2. Открыть Home Assistant и установить дополнение Mosquitto broker (если он не установлен) и интеграцию MQTT (если она не установлена).
  3. Настройки брокера можно оставить по умолчанию, но необходимо добавить пользователя для доступа к брокеру, для этого нужно перейти во вкладку "Люди" в Home Assistant и добавить пользователя.
  4. В приложении Polaris зайти в пункт "Настройки MQTT", сдвинуть переключатель "Включено", указать адрес Home Assistant (это и есть адрес брокера, если используете дополнение Mosquitto broker) и порт (по умолчанию 1883). Ниже ввести учётные данные созданного пользователя для доступа к mqtt брокеру, SSL не включать, и в верхнем правом углу нажать галочку, для сохранения настроек.

     <img src='https://github.com/user-attachments/assets/bed0ff7b-6322-4a4d-bc89-b3e7bbfacae1' width='200' alt='app screen 3: mqtt settings'>
     
  5. Зайти в HomeAssistant и установить интеграцию Polaris. Поскольку интеграции в репозитории HACS нет, то надо в ручную добавить этот репозиторий в HACS (три точки в верхнем правом углу).
  6. Добавить эту интеграцию в HomeAssistant (раздел Настройки - Интеграции) и в ней, добавить устройство. Оно определится автоматически, достаточно указать пространство.

Устройство так же может находиться во внешней сети, и если до сети с брокером есть маршрут, оно будет найдено.
</details>


## Устройства Polaris

| ID    | Модель           | Тип устройства | Поддержка | Функции | Изображение |
| :---: |------------------|----------------|-----------|---------|    :---:    |
|37|PWK -7111CGLD-WIFI-(old)|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/d/ec/850f5-5943-4845-bd40-0884cfd497f0/60.webp)
|245|PWK-0105|kettle|:heavy_check_mark:|volume, backlight, child_lock, water_tank, temperature, weight|![all](https://images.cdn.polaris-iot.com/a/c5/db790-4ed6-4dc6-a17b-639eb334e3ec/60.webp)
|205|PWK-1538CC|kettle|:heavy_check_mark:|night, volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/b/1c/2f620-bcdd-49a0-b321-c9e25433febd/60.webp)
|36|PWK-17107CGLD-WIFI-(old)|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/a6/0a0ae-769d-44cf-ae1d-039dad4be304/60.webp)
|29|PWK-1712CGLD|kettle|:heavy_check_mark:|child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/2/1e/87fb9-b3ab-4fc1-a184-1008e57064fb/60.webp)
|38|PWK-1712CGLD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/e/cc/ddf2f-070d-4867-8099-938bf6a3a084/60.webp)
|54|PWK-1712CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/e/cc/ddf2f-070d-4867-8099-938bf6a3a084/60.webp)
|59|PWK-1712CGLD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/0/80/2044e-71b1-4143-80f5-79ccf1dbff96/60.webp)
|63|PWK-1712CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/4/06/6d215-dfe6-4211-8260-8a72cb50f30e/60.webp)
|97|PWK-1712CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/1/4d/812d2-9cd5-473c-8670-865b6fa8cdbe/60.webp)
|117|PWK-1712CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/1c/4ff8e-7a0e-400c-9e50-43c6d45d300e/60.webp)
|208|PWK-1712CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/4/06/6d215-dfe6-4211-8260-8a72cb50f30e/60.webp)
|83|PWK-1712CGLD-RGB|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/e/cc/ddf2f-070d-4867-8099-938bf6a3a084/60.webp)
|244|PWK-1716CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|67|PWK-1720CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/6/41/04018-94b4-4ae7-be02-1375b22e39e2/60.webp)
|84|PWK-1720CGLD-RGB|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/6/41/04018-94b4-4ae7-be02-1375b22e39e2/60.webp)
|6|PWK-1725CGLD|kettle|:heavy_check_mark:|child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|52|PWK-1725CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|57|PWK-1725CGLD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|61|PWK-1725CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|86|PWK-1725CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/a/8c/aad08-4d13-489c-9b0f-028486297ac1/60.webp)
|105|PWK-1725CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|106|PWK-1725CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|177|PWK-1725CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|194|PWK-1725CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/a/8c/aad08-4d13-489c-9b0f-028486297ac1/60.webp)
|196|PWK-1725CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/a/8c/aad08-4d13-489c-9b0f-028486297ac1/60.webp)
|164|PWK-1728CGLDA|kettle|:heavy_check_mark:|night, speed, volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|209|PWK-1729CAD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/1e/63e7d-332e-42de-96a4-2b393463b78b/60.webp)
|189|PWK-1746CA|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/1e/63e7d-332e-42de-96a4-2b393463b78b/60.webp)
|8|PWK-1755CAD|kettle|:heavy_check_mark:|child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|53|PWK-1755CAD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|58|PWK-1755CAD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|62|PWK-1755CAD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|185|PWK-1755CAD|kettle|:heavy_check_mark:|volume, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/4/52/2f530-8ebb-426d-98d1-5922508ecbbc/60.webp)
|165|PWK-1755CAD-VOICE|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/96/c40d6-068b-4a17-9e9c-f912ee1e70c2/60.webp)
|121|PWK-1774CAD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|2|PWK-1775CGLD|kettle|:heavy_check_mark:|child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|51|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|56|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|60|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|98|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|188|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|223|PWK-1775CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, weight|![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|85|PWK-1775CGLD-SMART|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|139|PWK-1775CGLD-VOICE|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/8/08/f91f4-f117-4074-aa8a-d3d177d7c657/60.webp)
|175|PWK-1823CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/5/f2/5158d-edd3-4018-a391-2a97626f3bb9/60.webp)
|176|PWK-1841CGLD|kettle|:heavy_check_mark:|night, volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/5/cd/b1677-8f3f-4b28-8b8c-103756cd6c9f/60.webp)
|82|PWK-725CGLD|kettle|:heavy_check_mark:|volume, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/c/38/c5351-2643-4bcf-bd1b-c5d24a7a9b85/60.webp)
|147|PUH-0205|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/5/77/d82d4-6e9c-4794-8a6b-4d6893f9b297/60.webp)
|71|PUH-1010|humidifier|:heavy_check_mark:|speed, timer, volume, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/7/6d/75075-23c8-44c0-a582-d91919da426d/60.webp)
|72|PUH-2300|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/6/ee/0c47e-a3d6-4f99-840b-5a74f85e056e/60.webp)
|73|PUH-3030|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/3/a9/c2d1c-e416-45f5-8a7b-e2ac59c9b164/60.webp)
|75|PUH-4040|humidifier|:heavy_check_mark:|speed, timer, volume, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/0/79/caa3f-4b4d-4092-9a9e-c02ca79d8c4a/60.webp)
|99|PUH-4040|humidifier|:heavy_check_mark:|speed, timer, volume, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/0/79/caa3f-4b4d-4092-9a9e-c02ca79d8c4a/60.webp)
|153|PUH-4055|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/8/bc/dbc40-1588-48cd-80ce-3fa2c10c0d10/60.webp)
|137|PUH-4066|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/a/d3/3934a-32a1-44b5-b0f2-1be2951cb7d4/60.webp)
|157|PUH-4550|humidifier|:heavy_check_mark:|night, speed, timer, turbo, volume, ioniser, humidity, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/e/15/86a99-602c-4c6b-b204-43551b37d358/60.webp)
|158|PUH-6060|humidifier|:heavy_check_mark:|night, speed, timer, turbo, volume, ioniser, humidity, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/7/6f/07d82-8dea-42eb-b092-ae7a1bec1a22/60.webp)
|25|PUH-6090|humidifier|:heavy_check_mark:|speed, timer, volume, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/9/03/6eada-d5f2-4d60-bcfa-d4c9b2669852/60.webp)
|15|PUH-7406|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/2/49/d53fe-3e9d-4229-9900-8f621b54ca23/60.webp)
|87|PUH-8080/PUH-4606|humidifier|:heavy_check_mark:|speed, timer, volume, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/9/3a/2e628-d005-4ce2-be29-93aa56e1d315/60.webp)
|155|PUH-8802|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, |![all](https://images.cdn.polaris-iot.com/6/b1/2ddff-8f41-4fd2-8e33-6cfc60090332/60.webp)
|74|PUH-9009|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/a/a7/7bb37-25b8-4d03-99d2-775794af20dc/60.webp)
|4|PUH-9105/PUH-2709|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/9d/27f85-2e01-4cd7-85d8-a034e81c5be4/60.webp)
|17|PUH-9105/PUH-2709|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/9d/27f85-2e01-4cd7-85d8-a034e81c5be4/60.webp)
|18|PUH-9105/PUH-2709|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/9d/27f85-2e01-4cd7-85d8-a034e81c5be4/60.webp)
|44|PUH-9105/PUH-2709|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/9d/27f85-2e01-4cd7-85d8-a034e81c5be4/60.webp)
|70|PUH-9105/PUH-2709|humidifier|:heavy_check_mark:|speed, timer, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/9d/27f85-2e01-4cd7-85d8-a034e81c5be4/60.webp)
|1|EVO-0225|cooker|:heavy_check_mark:|timer, keep_warm, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/b/8f/ae138-e3b2-448a-8a8e-ca60eb7c3cc5/60.webp)
|95|PMC-00000|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|10|PMC-0521WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/1/31/fc82e-50af-430e-8d71-043bd7aeb5d2/60.webp)
|41|PMC-0521WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/1/31/fc82e-50af-430e-8d71-043bd7aeb5d2/60.webp)
|55|PMC-0524WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/e/5f/51204-817a-46fb-a477-c80cad89f019/60.webp)
|206|PMC-0524WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/3/32/d6c82-2ebc-4519-8b71-05de8097756a/60.webp)
|9|PMC-0526WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|40|PMC-0526WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|138|PMC-0526WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|39|PMC-0528WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/4/ce/e930f-5b1b-444f-96e2-04b4d9314231/60.webp)
|48|PMC-0528WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/4/ce/e930f-5b1b-444f-96e2-04b4d9314231/60.webp)
|47|PMC-0530WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/2/d9/64dfb-b93e-49b8-874c-766c212698c8/60.webp)
|210|PMC-0590AD|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/4/cc/bd7d5-385a-4edb-bb43-7a686dcffa2f/60.webp)
|215|PMC-5001WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/1/31/fc82e-50af-430e-8d71-043bd7aeb5d2/60.webp)
|79|PMC-5017WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/7/41/24cf9-cb91-431c-a5cb-183d2594a5af/60.webp)
|192|PMC-5017WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/7/41/24cf9-cb91-431c-a5cb-183d2594a5af/60.webp)
|80|PMC-5020WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/d/da/5a3c8-b17a-4d94-83cd-24bd2e8562d6/60.webp)
|77|PMC-5040WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/0/40/bbd11-87b7-47ae-9432-74b78d904d74/60.webp)
|78|PMC-5050WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/1/87/4d6af-60c0-48d3-8939-60400805fca9/60.webp)
|89|PMC-5055WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/a/67/edd4c-9a92-4cfe-b17e-53a76d282475/60.webp)
|114|PMC-5060 Smart Motion|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|240|PMC-5060 Smart Motion*|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|162|PMC-5063WIFI|cooker|:heavy_check_mark:|timer, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/e/5f/51204-817a-46fb-a477-c80cad89f019/60.webp)
|169|PPC-1505 Wi-FI|cooker|:heavy_check_mark:|timer, volume, pressure, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|183|PPC-1505 Wi-FI*|cooker|:heavy_check_mark:|timer, volume, pressure, keep_warm, child_lock, multi_step, delay_start, temperature, |![all](https://images.cdn.polaris-iot.com/6/fd/f7349-f7c0-46e0-b001-787923872799/60.webp)
|235|AM7310-(test)|coffeemaker|:x:|turbo, amount, volume, child_lock, water_tank, stream_warm, temperature, |![all](https://images.cdn.polaris-iot.com/d/05/16bab-b852-4e03-afa6-41a892d93205/60.webp)
|103|PACM-2080AC|coffeemaker|:x:|speed, amount, volume, weight, pressure, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/b/2b/8c952-9291-4c02-bce2-4d73f853452d/60.webp)
|200|PACM-2081AC|coffeemaker|:x:|speed, timer, amount, volume, weight, pressure, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/c/11/747d1-b6ce-417f-980d-665512b3a6ad/60.webp)
|166|PACM-2085GC|coffeemaker|:x:|speed, amount, volume, weight, pressure, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/b/2b/8c952-9291-4c02-bce2-4d73f853452d/60.webp)
|247|PCM-1255|coffeemaker|:x:|timer, amount, volume, weight, ioniser, child_lock, |![all](https://images.cdn.polaris-iot.com/6/7e/b8e87-9593-4023-b339-3fb6da5df931/60.webp)
|45|PCM-1540WIFI|coffeemaker|:x:|amount, volume, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/a/44/ec0b3-ea7f-4d75-bd2a-ba174bf1817d/60.webp)
|222|PCM-1540WIFI|coffeemaker|:x:|amount, volume, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/a/44/ec0b3-ea7f-4d75-bd2a-ba174bf1817d/60.webp)
|190|PCM-1560|coffeemaker|:x:|amount, volume, child_lock, water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/6/7e/b8e87-9593-4023-b339-3fb6da5df931/60.webp)
|207|PCM-2070CG|coffeemaker|:x:|turbo, amount, volume, child_lock, water_tank, stream_warm, temperature, |![all](https://images.cdn.polaris-iot.com/2/72/b2f22-3608-40b7-b435-7485fe68dfc2/60.webp)
|172|PAW-0804|air-cleaner|:x:|speed, timer, volume, backlight, |![all](https://images.cdn.polaris-iot.com/6/8d/81a02-893f-467d-a375-1c004bb31548/60.webp)
|140|PAW-0804(c3-test)|air-cleaner|:x:|speed, timer, turbo, volume, ioniser, backlight, |![all](https://images.cdn.polaris-iot.com/0/f0/440b3-27bd-49f8-81e4-0af6f8e13dee/60.webp)
|151|PPA-2025|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/5/de/94ac7-2530-446f-a4bd-566ddc4edd16/60.webp)
|203|PPA-2025|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/d/fb/9d0c9-ddaf-405a-8ae7-19b1ccf27fa3/60.webp)
|250|PPA-2025|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/d/fb/9d0c9-ddaf-405a-8ae7-19b1ccf27fa3/60.webp)
|152|PPA-4050|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/9/3d/a90f0-137c-414c-aa15-df9f395e1cb1/60.webp)
|204|PPA-4050|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/8/93/ca1e0-f8de-4b42-938f-6f803eb7d982/60.webp)
|251|PPA-4050|air-cleaner|:x:|speed, timer, volume, ioniser, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/8/93/ca1e0-f8de-4b42-938f-6f803eb7d982/60.webp)
|236|PPAT-02A|air-cleaner|:x:|speed, timer, turbo, volume, ioniser, humidity, backlight, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/a/87/e91a5-a8eb-4b7f-9d9d-88b7db5f744e/60.webp)
|238|PPAT-80P|air-cleaner|:x:|speed, timer, volume, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/f/66/2b72c-ed43-456e-9524-245e229bb667/60.webp)
|239|PPAT-90GDi|air-cleaner|:x:|speed, timer, turbo, volume, humidity, child_lock, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/f/66/2b72c-ed43-456e-9524-245e229bb667/60.webp)
|93|PHB-1350-WIFI|blender|:x:|speed, timer, multi_step, |![all](https://images.cdn.polaris-iot.com/e/f8/22f01-dd2f-40e3-8f85-d7dc8f9fddce/60.webp)
|35|PHB-1503-WIFI-(old)|blender|:x:|speed, timer, child_lock, multi_step, |![all](https://images.cdn.polaris-iot.com/3/a6/45180-5e03-4e43-9de9-a0948262c226/60.webp)
|34|PHB-1551-WIFI|blender|:x:|speed, timer, child_lock, multi_step, |![all](https://images.cdn.polaris-iot.com/e/f8/22f01-dd2f-40e3-8f85-d7dc8f9fddce/60.webp)
|31|ENIGMA-WI-FI|boiler|:x:|speed, timer, keep_warm, child_lock, smart_mode, temperature, |![all](https://images.cdn.polaris-iot.com/5/e6/60f0f-98be-44ea-bea4-42cc3a27d340/60.webp)
|11|PWH-IDF06|boiler|:x:|speed, timer, keep_warm, child_lock, smart_mode, temperature, |![all](https://images.cdn.polaris-iot.com/5/e6/60f0f-98be-44ea-bea4-42cc3a27d340/60.webp)
|249|RZBE|boiler|:x:|speed, volume, keep_warm, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/6/f1/21910-973b-4796-ab35-7bad5b9fb87e/60.webp)
|30|SIGMA-WI-FI|boiler|:x:|speed, timer, keep_warm, child_lock, smart_mode, temperature, |![all](https://images.cdn.polaris-iot.com/6/f1/21910-973b-4796-ab35-7bad5b9fb87e/60.webp)
|246|PRWC-3001|cleaner|:x:|turbo, water_tank, |![all](https://images.cdn.polaris-iot.com/f/91/8cc80-f16e-4ac8-b075-cdf8270801b6/60.webp)
|101|PVCR-0726-Aqua|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/20/da178-0a48-405d-83f5-c17300f23b5d/60.webp)
|108|PVCR-0726-GYRO|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/c/61/4b62b-f6f8-47fc-bd48-0112b56e9977/60.webp)
|21|PVCR-0735|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/9/89/721c8-9edb-49f0-8016-9b6fefb7b096/60.webp)
|163|PVCR-0735|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/9/89/721c8-9edb-49f0-8016-9b6fefb7b096/60.webp)
|19|PVCR-0833|cleaner|:x:|speed, find_me, |![all](https://images.cdn.polaris-iot.com/0/48/35580-64af-42e7-9994-55ef1407d591/60.webp)
|43|PVCR-0833|cleaner|:x:|speed, find_me, |![all](https://images.cdn.polaris-iot.com/0/48/35580-64af-42e7-9994-55ef1407d591/60.webp)
|104|PVCR-0905|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/6/de/c37ad-21d9-4f15-8c7f-ed8410babd7f/60.webp)
|156|PVCR-0905|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/f/eb/7cc05-b47a-4646-acc0-ad7d17ce8cc9/60.webp)
|107|PVCR-0926|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/20/da178-0a48-405d-83f5-c17300f23b5d/60.webp)
|23|PVCR-1028|cleaner|:x:|speed, battery, child_lock, |![all](https://images.cdn.polaris-iot.com/8/a3/68430-8088-404f-af1f-6d79cf4512d0/60.webp)
|22|PVCR-1050|cleaner|:x:|speed, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/4/ec/06465-b9e3-4e02-a27c-797fdcf182d1/60.webp)
|102|PVCR-1226-Aqua|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/20/da178-0a48-405d-83f5-c17300f23b5d/60.webp)
|109|PVCR-1226-GYRO|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/26/3ac2c-ce5a-4c4e-8f2b-d9cfc8653ed7/60.webp)
|24|PVCR-1229|cleaner|:x:|speed, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/25/f2359-b5a6-4e32-a1b5-88283a97c662/60.webp)
|68|PVCR-3100|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/4/80/6b6e6-6ecd-437e-b01c-2f14e2cf5b56/60.webp)
|7|PVCR-3200|cleaner|:x:|speed, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/4/27/7e198-dede-4ea1-a1a7-1cb9b6ce2888/60.webp)
|76|PVCR-3200|cleaner|:x:|speed, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/5/6d/bdc04-52f8-4092-a827-c1455e2a11f8/60.webp)
|115|PVCR-3200|cleaner|:x:|speed, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/5/6d/bdc04-52f8-4092-a827-c1455e2a11f8/60.webp)
|12|PVCR-3300|cleaner|:x:|speed, volume, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/5/7a/903fd-3c1e-4c17-a396-97d6a5eb32bd/60.webp)
|81|PVCR-3400|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/7/78/12125-b314-4cba-96dd-b394da015482/60.webp)
|130|PVCR-3600|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/6/24/ee896-0ec7-428c-8704-82f446107a45/60.webp)
|112|PVCR-3700|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/5/b6/684e6-a94d-4fc8-aa61-5a3efef92a92/60.webp)
|88|PVCR-3800|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/1/20/da178-0a48-405d-83f5-c17300f23b5d/60.webp)
|66|PVCR-3900|cleaner|:x:|speed, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/5/ba/bd543-ba02-4399-ac4a-be7bc65fd4d6/60.webp)
|131|PVCR-3900|cleaner|:x:|speed, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/5/ba/bd543-ba02-4399-ac4a-be7bc65fd4d6/60.webp)
|113|PVCR-4000|cleaner|:x:|speed, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/2/bb/d79e5-72a9-44f7-8921-46427cc4beab/60.webp)
|197|PVCR-4000|cleaner|:x:|speed, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/2/bb/d79e5-72a9-44f7-8921-46427cc4beab/60.webp)
|110|PVCR-4105|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/7/2f/6679a-5e9c-4aa1-81dd-80b370c34631/60.webp)
|127|PVCR-4105|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/7/2f/6679a-5e9c-4aa1-81dd-80b370c34631/60.webp)
|199|PVCR-4250|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/5/57/282da-d799-4c8d-80e6-dbd133cd9611/60.webp)
|241|PVCR-4250|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/e/ed/669b5-6fe6-4720-a6a1-aabc4f93fcee/60.webp)
|211|PVCR-4260|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/c/ce/591f4-223e-48b7-b01c-7d8efa0111c7/60.webp)
|142|PVCR-4500|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/9/38/99c96-80f5-4858-a1f1-322456498104/60.webp)
|195|PVCR-4500|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/e/6c/7638c-3e9c-4551-85e5-a0b9138961cd/60.webp)
|119|PVCR-5001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f2/f2957-fb7e-4ac4-b644-8eedfeff61d7/60.webp)
|146|PVCR-5001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f2/f2957-fb7e-4ac4-b644-8eedfeff61d7/60.webp)
|154|PVCR-5001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f2/f2957-fb7e-4ac4-b644-8eedfeff61d7/60.webp)
|201|PVCR-5003|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/9/19/84a49-0f78-40d1-9f6c-c3ad1c77c8ae/60.webp)
|242|PVCR-5005|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/8/6b/1da86-4db7-4410-93a7-f0b952d8eb1c/60.webp)
|123|PVCR-6001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f7/b2aa9-56ab-4ef0-b19e-bc78c9492809/60.webp)
|148|PVCR-6001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f7/b2aa9-56ab-4ef0-b19e-bc78c9492809/60.webp)
|221|PVCR-6001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f7/b2aa9-56ab-4ef0-b19e-bc78c9492809/60.webp)
|187|PVCR-6003|cleaner|:x:|speed, turbo, volume, find_me, backlight, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/f/4f/8dec1-d948-4d6c-b09c-e8cfe71f0408/60.webp)
|128|PVCRAC-7050|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/6/a8/f5bc0-5cb6-423a-b51e-34e02b1dcd9d/60.webp)
|212|PVCRAC-7290|cleaner|:x:|speed, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/6/29/e24f4-d9b1-4579-b524-f2d875b627e5/60.webp)
|178|PVCRAC-7750|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/d/70/0218c-9a0e-4d00-b104-3979316f231c/60.webp)
|198|PVCRAC-7790|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/3/21/b6739-f68c-4039-86a0-bdd72c4daf5b/60.webp)
|126|PVCRDC-0101|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/a/e3/2643f-16a9-445a-bef6-67e2990b95b2/60.webp)
|160|PVCRDC-0101|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, |![all](https://images.cdn.polaris-iot.com/1/9b/495af-1edb-42f6-9d07-ea6dff1327b9/60.webp)
|124|PVCRDC-5002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/5/da/761dd-4d18-4958-89e5-cb391aa3238c/60.webp)
|149|PVCRDC-5002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/5/da/761dd-4d18-4958-89e5-cb391aa3238c/60.webp)
|213|PVCRDC-5002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/5/da/761dd-4d18-4958-89e5-cb391aa3238c/60.webp)
|202|PVCRDC-5004|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/c/10/8ae2a-7f37-46e6-8f46-c2f9c0d916eb/60.webp)
|181|PVCRDC-5006|cleaner|:x:|speed, turbo, volume, find_me, ioniser, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/8/32/4dc97-320a-4f52-92b7-a188ac71c434/60.webp)
|125|PVCRDC-6002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/d/e6/0b12b-1c6d-4143-a7f1-acaf586d0499/60.webp)
|150|PVCRDC-6002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/d/e6/0b12b-1c6d-4143-a7f1-acaf586d0499/60.webp)
|186|PVCRDC-6004|cleaner|:x:|speed, turbo, volume, find_me, ioniser, backlight, water_tank, stream_warm, |![all](https://images.cdn.polaris-iot.com/9/5f/5f965-16b3-4c8c-a449-bd8a0a3a476b/60.webp)
|217|PVCRDC-G2-5002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/c/40/4bdb3-7ccb-4b2e-b131-835d0c563624/60.webp)
|218|PVCRDC-G2-6002|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/7/1e/9eaa3-227e-4fb2-92bf-cb969f7db86e/60.webp)
|133|PVCR-G2-0726W|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/1/bd/019c4-56b4-4986-a037-81dd7c5db320/60.webp)
|193|PVCR-G2-0826|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/2/de/d787e-8ca3-4a1b-aeee-c192c7986381/60.webp)
|134|PVCR-G2-0926W|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/2/d1/933a9-c624-449e-b0e9-a66638fbab63/60.webp)
|135|PVCR-G2-1226|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/d/94/beec6-89df-4e44-a943-eba7cc79bfde/60.webp)
|129|PVCR-G2-3200|cleaner|:x:|speed, turbo, volume, battery, find_me, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/f/00/a072d-69a7-44d3-93ad-26061cc2251f/60.webp)
|122|PVCR-G2-3600|cleaner|:x:|speed, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/6/24/ee896-0ec7-428c-8704-82f446107a45/60.webp)
|219|PVCR-G2-5001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f2/f2957-fb7e-4ac4-b644-8eedfeff61d7/60.webp)
|220|PVCR-G2-6001|cleaner|:x:|speed, turbo, volume, find_me, water_tank, |![all](https://images.cdn.polaris-iot.com/8/f2/f2957-fb7e-4ac4-b644-8eedfeff61d7/60.webp)
|100|PVCR-Wave-15|cleaner|:x:|speed, turbo, battery, child_lock, water_tank, |![all](https://images.cdn.polaris-iot.com/7/4d/dbdab-a1ec-46e0-a669-57e4e4c24ae8/60.webp)
|111|PVCS-1150|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/1/27/36f11-5225-478f-bbc2-fed844a33639/60.webp)
|90|PVCS-2090|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/3/9d/8bcaf-38fa-4168-b71e-cf201171e719/60.webp)
|136|PVCS-4070|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|229|PVCS-4070|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|232|PVCS-6020|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|230|PVCS-8200|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|234|PVCSDC-3000|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|233|PVCSDC-3005|cordless_cleaner|:x:|speed, timer, |![all](https://images.cdn.polaris-iot.com/0/5c/3078f-88c4-4f8b-8bbf-7a1f1db794fd/60.webp)
|180|PSF-3315|fan|:x:|speed, timer, turbo, amount, volume, child_lock, smart_mode, |![all](https://images.cdn.polaris-iot.com/0/b0/6a48d-34d0-4ca9-b6da-13836486400b/60.webp)
|248|PSF-4025|fan|:x:|speed, timer, volume, child_lock, |![all](https://images.cdn.polaris-iot.com/0/b0/6a48d-34d0-4ca9-b6da-13836486400b/60.webp)
|5|PWS1830/1883|floor-scales|bluetooth||![all](https://images.cdn.polaris-iot.com/f/cc/49dba-e496-44af-9d44-a657109675c5/60.webp)
|3|PWS18XX|floor-scales|bluetooth|weight|![all](https://images.cdn.polaris-iot.com/2/16/8d351-214b-4c16-8c52-09a4e9b568a6/60.webp)
|167|Scales-collection|floor-scales|bluetooth||![all](https://images.cdn.polaris-iot.com/f/c4/584c3-3ee5-4f5f-bee7-10b99626a70c/60.webp)
|141|SLG-V3|generator|bluetooth||![all](https://images.cdn.polaris-iot.com/4/14/8b312-c022-494a-86ce-0091e37168f2/60.webp)
|144|SLG-V4|generator|bluetooth||![all](https://images.cdn.polaris-iot.com/4/14/8b312-c022-494a-86ce-0091e37168f2/60.webp)
|179|PGP-3010-SMOKELESS|grill|:x:|speed, timer, turbo, child_lock, |![all](https://images.cdn.polaris-iot.com/2/ea/c9dfe-cd3d-4f04-bd55-67b14f6e8c84/60.webp)
|96|PGP-4001|grill|:x:|timer, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/6/71/a0394-5753-4bd7-abcc-963f34fb79a9/60.webp)
|120|PHD-4000|hair_care|:x:|speed, stream_warm, temperature, |![all](https://images.cdn.polaris-iot.com/b/6c/73ab1-d25f-44d7-98a7-7f91e6d40628/60.webp)
|184|PHS-1300|hair_care|:x:|child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/7/97/7f835-fabd-4221-b90c-f32cf4a5bd1d/60.webp)
|171|PHSB-5000DF|hair_care|:x:|speed, pressure, water_tank, stream_warm, temperature, |![all](https://images.cdn.polaris-iot.com/4/54/d75e0-7363-4aad-8f8e-e55d83052fd9/60.webp)
|145|PHSC-1234|hair_care|:x:|ioniser, humidity, temperature, |![all](https://images.cdn.polaris-iot.com/2/fe/425f6-be9b-47ca-a34b-5fc12dbf8443/60.webp)
|46|PCH-0320WIFI|heater|:x:|timer, temperature, |![all](https://images.cdn.polaris-iot.com/2/ef/6cb11-25b4-4c82-adcf-33f0e01302b8/60.webp)
|65|PCH-0320WIFI|heater|:x:|timer, temperature, |![all](https://images.cdn.polaris-iot.com/2/ef/6cb11-25b4-4c82-adcf-33f0e01302b8/60.webp)
|16|PHV-1401|heater|:x:|timer, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/e/3b/3615d-0d9d-4107-9783-df4e9655cdd1/60.webp)
|49|PMH-21XX|heater|:x:|timer, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/2/30/eb6b9-5ed3-4536-9e54-b380fd25c178/60.webp)
|64|PMH-21XX|heater|:x:|timer, backlight, child_lock, temperature, |![all](https://images.cdn.polaris-iot.com/6/e0/263c0-2c33-4a8a-929c-e998568a5606/60.webp)
|91|PIR-2624AK-3m|iron|:x:|timer, child_lock, |![all](https://images.cdn.polaris-iot.com/d/ab/4f72f-088f-44fe-9f78-81c36244a657/60.webp)
|161|PIR-3074SG|iron|:x:|speed, timer, volume, humidity, child_lock, |![all](https://images.cdn.polaris-iot.com/d/ab/4f72f-088f-44fe-9f78-81c36244a657/60.webp)
|173|PIR-3210AK-3m|iron|:x:|speed, timer, volume, child_lock, |![all](https://images.cdn.polaris-iot.com/d/ab/4f72f-088f-44fe-9f78-81c36244a657/60.webp)
|174|PIR-3225AK-3m|iron|:x:|speed, timer, turbo, volume, humidity, child_lock, |![all](https://images.cdn.polaris-iot.com/4/d1/793cf-adc8-4342-9e5d-447a0c8b1724/60.webp)
|191|PSS-2002K|iron|:x:|volume, child_lock, stream_warm, |![all](https://images.cdn.polaris-iot.com/f/e8/84ba2-8592-412d-b067-ce36ad9442d4/60.webp)
|159|PSS-9090K|iron|:x:|speed, turbo, volume, child_lock, stream_warm, temperature, |![all](https://images.cdn.polaris-iot.com/4/ba/f6029-12bf-4598-87e0-06a4ca6fe68b/60.webp)
|132|PWF-2005|irrigator|:x:|speed, timer, ioniser, smart_mode, |![all](https://images.cdn.polaris-iot.com/5/bd/1a68b-9fb5-46e9-acbd-c086748b72bb/60.webp)
|252|PWF-2005|irrigator|:x:|speed, timer, ioniser, smart_mode, |![all](https://images.cdn.polaris-iot.com/5/bd/1a68b-9fb5-46e9-acbd-c086748b72bb/60.webp)
|32|PMG-2580|meat_grinder|:x:|speed, turbo, volume, child_lock, |![all](https://images.cdn.polaris-iot.com/7/68/d874e-389d-49e6-8901-705740dbedc8/60.webp)
|216|PMG-3060|meat_grinder|:x:|speed, timer, volume, child_lock, |![all](https://images.cdn.polaris-iot.com/f/47/83e05-570f-4ccd-9455-612611d6568c/60.webp)
|237|SM-8095|multicooker|:x:|speed, timer, backlight, child_lock, weight|![all](https://images.cdn.polaris-iot.com/c/da/ab2e1-775a-4bc4-9a18-fe004ffafdc7/60.webp)
|116|Smart-Lid|other|:x:|speed, battery, |![all](https://images.cdn.polaris-iot.com/f/fc/274e8-7ddf-4429-b827-f63b141c6db9/60.webp)
|182|Voice-Ring|other|bluetooth||![all](https://images.cdn.polaris-iot.com/8/bd/13c34-6bbb-49e4-a6fd-d025424db590/60.webp)
|170|Watch|other|bluetooth||![all](https://images.cdn.polaris-iot.com/c/a2/d9565-3316-4613-9b02-5ec661fc15d6/60.webp)
|92|PGS-1450CWIFI|steamer|:x:|speed, child_lock, |![all](https://images.cdn.polaris-iot.com/1/00/43d2d-5a4b-4de7-a60a-767a007b7f5c/60.webp)
|94|PSS-7070KWIFI|steamer|:x:|water_tank, temperature, |![all](https://images.cdn.polaris-iot.com/1/00/43d2d-5a4b-4de7-a60a-767a007b7f5c/60.webp)
|50|PETB-0202TC|toothbrush|:x:|timer, smart_mode, |![all](https://images.cdn.polaris-iot.com/d/d5/14363-6a8e-4d0d-bee1-658994b95305/60.webp)
