from django.contrib import admin
from users.model.profile import (
                                    UserProfile,
                                    IPUser,
                                    OneUserLocation,
                                    TwoUserLocation,
                                    ThreeUserLocation,
                                )
from users.model.list import Subscribe, Guest, UserBlock
from django.conf import settings
from users.models import User


admin.site.register(User)

admin.site.register(UserProfile)
admin.site.register(IPUser)
admin.site.register(OneUserLocation)
admin.site.register(TwoUserLocation)
admin.site.register(ThreeUserLocation)

admin.site.register(Subscribe)
admin.site.register(Guest)
admin.site.register(UserBlock)
