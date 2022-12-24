from django.db import models
from django.contrib.auth.models import AbstractUser


# cоздадим кастомную модель пользователя на основе класса AbstractUser
# выбираем именно этот встроенный класс,
# так как нас устраиваю поля, которые уже есть у этого класса, но
# нам нужно расширить встроенную пользовательскую модель
# - добавить новые поля
# - переопределить некоторые поля
# указываем поля модели User согласно документации апи

class User(AbstractUser):
    """Настраиваемая модель пользователя"""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )

    # поле username представляет собой строковое обозначение имени пользователя
    # и по ТЗ есть ограничение по длине, укажем его
    # также это поле должно быть уникальным, тоже укажем это в аттрибутах
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True
    )
    # для поля email также укажем ограничение по длине и уникальность
    email = models.EmailField(
        verbose_name='Электронная почта пользователя',
        max_length=254,
        unique=True
    )
    # # следующие два поля - строковые,
    # # у обоих нужно указать ограничение по длине по ТЗ
    # first_name = models.CharField(
    #     max_length=150
    # )
    # last_name = models.CharField(
    #     max_length=150,
    # )

    # следующее поле bio может быть достаточно объемным, так как это биография,
    # описание поэтому выбираем тип поля TextField
    # ограничения по длине не указываем
    # кроме того, это поле необязательное для заполнения,
    # поэтому укажем соответствующие аттрибуты - blank и null
    bio = models.TextField(
        verbose_name='Биография пользователя',
        blank=True,
        null=True
    )
    # следующее поле роль пользователя. Оно строковое, выбираем тип CharField
    # кроме того,, по умолчанию оно = user. Укажем это в аттрибутах
    # также поле role должно позволять выбрать одну из ролей
    role = models.CharField(
        verbose_name='Роль пользователя',
        default=USER,
        choices=ROLE_CHOICES

    )


# создаем модель категорий произведений
# у нее будет 2 поля - название категории и ее идентификатор
class Category(models.Model):
    """Модель категории произведения"""
    name = models.CharField(
        verbose_name='Название категории',
        # по ТЗ есть ограничение длины этого текстового поля,
        # указываем это в параметре max_length
        max_length=256
    )
    # поле slug должно быть уникальным,
    # поэтому указываем в параметрах unique = True
    # Также по ТЗ есть ограничение длины этого текстового поля,
    # указываем это в параметре max_length
    slug = models.SlugField(
        verbose_name='Идентификатор категории',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# создаем модель жанров произведений
# у нее также два поля - название жанра и его идентификатор
class Genre(models.Model):
    """Модель жанра произведения"""
    name = models.CharField(
        verbose_name='Название жанра',
        # по ТЗ есть ограничение длины этого текстового поля,
        # указываем это в параметре max_length
        max_length=256
    )

    # поле slug должно быть уникальным,
    # поэтому указываем в параметрах unique = True
    # Также по ТЗ есть ограничение длины этого текстового поля,
    # указываем это в параметре max_length
    slug = models.SlugField(
        verbose_name='Идентификатор жанра',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения"""
    # по ТЗ есть ограничение длины этого текстового поля,
    # указываем это в параметре max_length
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=256
    )

    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year]
    )

    description = models.TextField(
        verbose_name='Описание произведения',

        # добавляем опцию для поля - blank
        # т.е есть возможность добавлять произведение без описания
        # это поле не является обязательным cогласно ТЗ
        blank=True
    )

    # Т.к по ТЗ одно произведение может быть привязано
    # только к одной категории,
    # то используем тип поля ForeignKey(cвязь один-ко-многим)
    # поле category определяем как внешний ключ.
    # Оно будет хранить идентификатор категории этого произведения
    # т.е поле category представляет собой
    # отношение к другой таблице - Category
    # согласно ТЗ при удалении объекта категории Category
    # не нужно удалять связанные с этой категорией произведения
    # для этого в указываем параметр on_delete = models.SET_NULL
    # Этот параметр определяет, должно ли происходить удаление.
    # Он сообщает, что делать, когда родительское значение удалено.
    # Для нашего случая категория будет удаляться
    # без удаления связанного произведения
    category = models.ForeignKey(
        Category,
        related_name='titles',
        verbose_name='Категория произведения',
        on_delete=models.SET_NULL,
        null=True
    )

    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    # Так как одно произведение может быть привязано к нескольким жанрам,
    #  то используем тип поля ManyToMany
    # поле genre представляет собой отношение к другой таблице Genre
    # в конструктор models.ManyToMany передаем модель,
    # с которой установливаются отношения
    # "многие-ко-многим" - модель Жанра
    # в итоге между 2-мя этими таблицами(Title и Genre)
    # будет создана промежуточная таблица,
    #  через которую и будет осуществляться связь

    # согласно ТЗ при удалении объекта жанра Genre
    # не нужно удалять связанные с этим жанром произведения
    # для этого в указываем параметр on_delete = models.SET_NULL
    # Этот параметр определяет, должно ли происходить удаление.
    # Он сообщает, что делать, когда родительское значение удалено.
    # Для нашего случая жанр будет удаляться
    # без удаления связанного произведения
    # указываем параметр blank = True,
    # чтобы была возможность создавать экземпляры модели Title без категории

    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр произведения',
        # в качестве дополнительного парамметра указываем throught
        #  здесь указываем промежуточную модель,
        # через которую обеспечивается связь
        # многие ко многим между моделями Title и Genre
        through='GenreTitle'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


# промежуточная модель между моделями Title и Genre
# в ней будут 2 поля - title и genre
class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

    def __str__(self):
        return f'{self.title}, {self.genre}'
