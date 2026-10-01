import sqlalchemy as sa

def force_instant_defaults(mapper=None):
    """
    Function that assigns object column defaults on object initialization
    time. By default calling this function applies instant defaults to all
    your models.

    Setting up instant defaults::


        from sqlalchemy_utils import force_instant_defaults


        force_instant_defaults()

    Example usage::


        class Document(Base):
            __tablename__ = 'document'
            id = sa.Column(sa.Integer, autoincrement=True)
            name = sa.Column(sa.Unicode(50))
            created_at = sa.Column(sa.DateTime, default=datetime.now)


        document = Document()
        document.created_at  # datetime object


    :param mapper: The mapper which the automatic instant defaults forcing
                   should be applied to
    """
    if mapper is None:
        mapper = sa.orm.Mapper
    sa.event.listen(mapper, 'init', instant_defaults_listener)


def instant_defaults_listener(target, args, kwargs):
    # insertion order of kwargs matters
    # copy and clear so that we can add back later at the end of the dict
    original = kwargs.copy()
    kwargs.clear()

    for key, column in sa.inspect(target.__class__).columns.items():
        if hasattr(column, 'default') and column.default is not None:
            if not hasattr(column.default, 'arg'):
                continue
            elif callable(column.default.arg):
                kwargs[key] = column.default.arg(target)
            else:
                kwargs[key] = column.default.arg

    # supersede w/initial in case target uses setters overriding defaults
    kwargs.update(original)