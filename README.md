![](RackMultipart20231107-1-3eg5z5_html_53d1e378b299ba4c.png)

![](RackMultipart20231107-1-3eg5z5_html_1a8dddf43e63d360.png)
 ![Shape1](RackMultipart20231107-1-3eg5z5_html_b861174202058472.gif)

# **MatchScore**

# Organize and manage tournaments and leagues

# Project Description

Tournament directors have long needed a solution that will streamline the organization and management of sport events. MatchScore aims to solve that problem by providing all the tools required.

## Features:

- Organizing events
  - Match– a one-off event
  - Tournament – knockout or league format
- Managing events
  - Mark the score
  - Change the date
  - Update the participants
- Player profiles
  - Name, Country, Sports Club
- Score tracking
  - Tournament and player statistics
- Registration
  - Allows event organization and management (if approved)
  - Associate with player profile

# Instructions how to use the application:

Ще ви се създадат 2 потребителя при стартирането на програмата:

username: 'director@director.com'
pass:'test', 
role:'director'

user2:'admin@director.com',
pass:'test',
role:'admin'

1. Потребител  / User

      1)	Register User:
          a.	За регистрация се изисква следната информация в бодито:
          {
            "email": "user@example.com",
            "password": "string"
          }
      При успешна регистрация връща токен.

      2)	Log-in:
          Очаквана информация в бодито:
          {
            "email": "Director@example.com",
            "password": "test"
          }

      3)	Promote to director:
          a.	Изпраща заявка за смяна на ролята;
          b.	Нужно е само да се посочи токена в хедъра и да се изпрати заявка;

      4)	Make request - Изпращане на заявка за линкване на Потребител с Профил на играч:
          С токена в хедъра се подава:
          {
            "player_id": 1
          }
          Output:
          Request sent

2. Админ/ Admin:

      1)	Get all(requests):
      За целта трябва да сте с user_role Админ. Можете да видите всички заявки, които са регистрирани.
      Имате възможност да филтрирате търсенето по user_id или дали заявката е одобрена или не(query param). Да не забравите да посочите токен.
      При успешен Request би трябвало да получите следния отговор, ако има данни в базата:
          [
            {
              "id": 1,
              "request": "player_profile link",
              "user_id": 2,
              "player_id": 1
            },
            {
              "id": 4,
              "request": "Director",
              "user_id": 3,
              "player_id": null
            }
          ]

      2)	Director promotion - Обработване на завките за Директор:
      a.	В бодито посочвате:
            {
              "user_id": 0,
              "approved": 0
            }
        	Като approved ще търси True или False (1,0)

      3) Link profile - Обработване на заявките за линкване на потребител с играч на профил:
      Очакван инпут:
          {
            "user_id": 0,
            "player_id": 0,
            "approved": 0
          }

      4) Смяна на ролята:
        Този ендпоинт е служебен и служи за спешна смяна на ролята на един юзър. Където не се пращат заявки за целта, а директно се сменя. User_id(path) и new_role(query) са задължителни полета.

3. Player/Играч:

      1)	Преглед на играч по ID:
          a)	Не е нужен токен;
          b)	Само се посочва номера на играча(path param) и връща цялата статистика на играча;

      2)	Редактиране на играч:
          a)	Само директор може да редактира данните на един играч, но само ако играчът не е свързан за потребител. Ако е свързан - само този потребител(играч) може да си редактира данните. Очакваните данни са следните:
              {
                "new_name": "string",
                "new_country": "string",
                "new_club": "string"
              }
          Всички полета са задължителни, ако има полета където няма промяна, въвеждате същите данни;
          Посочва се и player_id като path param.

      3)	Създаване на нов играч:
          a)	Тука е нужно да се подава токен в хедъра и трябва да сте Директор.
          i)	Очаквана информация в бодите е следната:
              {
                "full_name": "string",
                "country": "string",
                "sport_club": "string"
              }

4. Tournaments/Турнири:
      1)	Get All Tournaments – Връща всички налични турнири. Токенът не е задължителен;
            a)	Наличен филтръ – име на турнира или формат на турнира(‘League’, ‘Knockout’) като query params.	

      2)	Create tournament:
      	В бодито се посочва:
          a.	името на турнира;
          b.	формата на турнира – “League” или “Knockout”;
          c.	парична награда int;
          d.	Формат на мача – “Score limit: {int}” или “Time limit: {int} minutes”;
          e.	Участници;
          f.	Начална дата на турнира;

        Пример:
              {
                "title": "New Cup 2025",
                "tour_format": "Knockout",
                "prize": 20,
                "match_format": "Time limit:5",
                "participants": ["McGregor", "Anton Angelov", "Kubrat Pulevro", "John Johns"],
                "start_date": "2023-12-06"
              }

              Output:
              {
                "title": "New Cup 2025",
                "tour_format": "Knockout",
                "prize": 20,
                "match_format": "Time limit:5",
                "participants": [
                  "Shaho",
                  "Anton Angelov",
                  "Kubrat Puevro",
                  "John Johns"
                ],
                "id": 4,
                "scheme_format": "semi-final",
                "matches": [
                  {
                    "id": 8,
                    "player_1": "Shaho",
                    "player_2": "John Johns",
                    "date": "2023-12-06T00:00:00"
                  },
                  {
                    "id": 9,
                    "player_1": "Kubrat Puevro",
                    "player_2": "Anton Angelov",
                    "date": "2023-12-06T00:00:00"
                  }
                ],
                "start_date": "2023-12-06",
                "winner": "Awaiting winner"
              }

      3)	Get League Ranking
          a)	Посочва се номера на турнира като path param

      4)	Get tournament by ID:
          a)	Посочва се номера на турнира като path param

      5)	Manage tournament:
          a)	подава се ном. на турнира като path param и в бодите в правкт текст се подава новата дата в следния формат:
          "2023-12-06"

      6)	Manage participants:
          a)	В този ендпоинт е възможна смяната на играчи.
          b)	Като path param се подава ном. на турнира и в бодите играчите:
              {
                "old_player": "string",
                "new_player": "string"
              }

5. Matches/Мачове:

      1)	Get all matches:
      	Възможни филтри:
          a.	sort – ‘asc’ & ‘desc’;
          b.	sort_by – ‘date’ & ’tournament_id’;
          c.	page – страница номер;
          d.	page_size – големина на страницата(по дефолт е 2)

      2)	Get match by ID:
          a)	Match_id като path param

      3)	Set match Date:
          a)	Подава се ном. на мача като path param;
          b)	След което в бодито се подава дата и час в следния формат:
                {
                  "date": "2023-12-06 21:47:20"
                }

      4)	Set Match Score:
          a)	Първо трябва да се въведат дати на мачовете от съответния ендпоинт.
          b)	Подава се номера на мача като path param.
          c)	В бодито се въвежда резултати и дали мачът е завършил( True, False):
                {
                  "pl_1_score": 1,
                  "pl_2_score": 2,
                  "match_finished": ‘false’ или ‘true’
                }
        Да се има предвид, че въвеждането на резултата  става чрез събиране. Тоест въведените точки в бодито + вече съществуващите точки в базата. Ако веднъж е въведен резултат 2:1, то при следващо въвеждане на резултат 1:1 ще се получи 3:2.

      След като се изиграе финал, принтира победителя:
            {
              "champion_name": "Djokovic",
              "club": TC Balkan,
              "country": Serbia,
              "tournament_won": "New Cup 2023"
            }

      5)	Get matches by tournament ID:
          a)	Подава се ном. на турнира като path param. и показва всички мачове в този турнир.
    

# Използвани инструменти и технологии:
  MariaDB
  FastApi
  PyJWT
  Bcrypt
  Python-dotenv
  Mailjet-rest
  Linode