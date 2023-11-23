import functools

from maya import cmds


class ContextDecorator:

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with self:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    raise e

        return wrapper

    def __enter__(self):
        raise NotImplementedError('"__enter__" method must be implemented !')

    def __exit__(self, type_, value_, traceback_):
        if any((type_, value_, traceback_)):
            print('++++++++++++++++++++', type_, value_, traceback_)
            raise value_ from None
        return True


class QDDisableRefresh(ContextDecorator):

    kDisableCount = 0

    def __enter__(self):
        if QDDisableRefresh.kDisableCount == 0:
            cmds.refresh(suspend=True)
        QDDisableRefresh.kDisableCount += 1

    def __exit__(self, *args):
        QDDisableRefresh.kDisableCount = max(QDDisableRefresh.kDisableCount - 1, 0)
        if QDDisableRefresh.kDisableCount == 0:
            cmds.refresh(suspend=False)
        return super().__exit__(*args)
