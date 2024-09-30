from cloudinary_storage.storage import StaticHashedCloudinaryStorage

class FixedStaticHashedCloudinaryStorage(StaticHashedCloudinaryStorage):
    def url(self, name):
        url = super().url(name)
        return url.replace('%5C', '/')

    def _normalize_name(self, name):
        name = super()._normalize_name(name)
        return name.replace('\\', '/')
