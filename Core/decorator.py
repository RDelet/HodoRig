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
        raise NotImplementedError(f"{ContextDecorator}.__enter__ method must be implemented !")

    def __exit__(self, type_, value_, traceback_):
        if any((type_, value_, traceback_)):
            # ToDo: Log error
            raise value_ from None
        return True


class DisableRefresh(ContextDecorator):

    kDisableCount = 0

    def __enter__(self):
        if self.kDisableCount == 0:
            cmds.refresh(suspend=True)
        self.kDisableCount += 1

    def __exit__(self, *args):
        self.kDisableCount = max(self.kDisableCount - 1, 0)
        if self.kDisableCount == 0:
            cmds.refresh(suspend=False)

        return super().__exit__(*args)


class DisableCacheEvaluation(ContextDecorator):

    kDisableCount = 0

    def __init__(self):
        super().__init__()
        self._state = cmds.evaluator(query=True, name='cache', enable=True)
        self._plugin_loaded = cmds.pluginInfo('cacheEvaluator', query=True, loaded=True)

    def __enter__(self):
        if DisableCacheEvaluation.kDisableCount == 0 and self._plugin_loaded:
            cmds.evaluator(name='cache', enable=False)
            cmds.cacheEvaluator(flushCache='destroy')
        DisableCacheEvaluation.kDisableCount += 1

    def __exit__(self, *args):
        DisableCacheEvaluation.kDisableCount = max(DisableCacheEvaluation.kDisableCount - 1, 0)
        if DisableCacheEvaluation.kDisableCount == 0 and self._plugin_loaded:
            cmds.evaluator(name='cache', enable=self._state)

        return super().__exit__(*args)


class UndoChunk(ContextDecorator):

    def __init__(self, chunk_name='UndoChunk'):
        super().__init__()
        self._chunk_name = chunk_name

    def __enter__(self):
        if not cmds.undoInfo(query=True, chunkName=True):
            cmds.undoInfo(openChunk=True, chunkName=self._chunk_name)

    def __exit__(self, *args):
        if cmds.undoInfo(query=True, chunkName=True) == self._chunk_name:
            cmds.undoInfo(closeChunk=True)
