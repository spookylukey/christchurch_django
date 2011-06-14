from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class SermonsApp(CMSApp):
    name = "Sermon App"
    urls = ["sermons.urls"]

apphook_pool.register(SermonsApp) # register your app
