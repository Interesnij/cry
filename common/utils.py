def get_current_form(number):
    if number in [1,2]:
        from ad_posts.forms import Form_1
        form = Form_1
        return form
    elif number in [3,4,5,6]:
        from ad_posts.forms import Form_2
        return Form_2
    elif number in [7,8,9,10,11,12,13,14,15,16]:
        from ad_posts.forms import Form_3
        return Form_3
    elif number in [17,18,19,20,21,22,23,24,25,26,27,28]:
        from ad_posts.forms import Form_4
        return Form_4
    elif number in [29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44]:
        from ad_posts.forms import Form_5
        return Form_5
    elif number in [45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62]:
        from ad_posts.forms import Form_6
        return Form_6
    elif number in [63,64,65,66,67,68,69,70,71,72,73,74,75,76,77]:
        from ad_posts.forms import Form_7
        return Form_7
    elif number in [78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94]:
        from ad_posts.forms import Form_8
        return Form_8
    elif number in [95,96,97,98,99,100,101,102,103,104,105,106]:
        from ad_posts.forms import Form_9
        return Form_9
    elif number in [107,108,109,110,111,112,113,114,115]:
        from ad_posts.forms import Form_10
        return Form_10
    elif number in [116,117,118,119,120,121,122,123,124,125]:
        from ad_posts.forms import Form_11
        return Form_11
    elif number in [126,127,128,129,130,131,132,133,134,135,136]:
        from ad_posts.forms import Form_12
        return Form_12
    elif number in [137,138,139,140,141,142,143,144,145,146,147,148]:
        from ad_posts.forms import Form_13
        return Form_13
    elif number in [149,150,151,152,153,154,155,156,157,158,159,160,161]:
        from ad_posts.forms import Form_14
        return Form_14
    elif number in [162,163,164,165,166,167,168,169,170,171,172,173,174,175]:
        from ad_posts.forms import Form_15
        return Form_15
    elif number in [176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191]:
        from ad_posts.forms import Form_16
        return Form_16
    elif number in [192,193,194,195,196,197,198,199,200,201,202]:
        from ad_posts.forms import Form_17
        return Form_17
    elif number in [203,204,205,206,207,208,209,210,211,212,213,214]:
        from ad_posts.forms import Form_18
        return Form_18
    elif number in [215,216,217,218,219,220,221,222,223,224,225,226,227,228,229]:
        from ad_posts.forms import Form_19
        return Form_19
    elif number in [230,231,232,233,234,235,236,237,238,239,240]:
        from ad_posts.forms import Form_20
        return Form_20
    elif number in [241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269]:
        from ad_posts.forms import Form_21
        return Form_21
    elif number in [270,271,272,273,274,275,276,277,278]:
        from ad_posts.forms import Form_22
        return Form_22
    elif number in [279,280]:
        from ad_posts.forms import Form_23
        return Form_23


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def last_ads_for_russia():
    from ad_posts.models import Ad
    from django.db.models import Q

    ads_query = Q(city__region__country__id=1, creator__is_blocked=False, is_deleted=False, is_active=True)
    ads = Ad.objects.filter(ads_query)
    return ads[:21]

def last_courses_for_russia():
    from skill_posts.models import Course
    from django.db.models import Q

    ads_query = Q(creator__is_blocked=False, is_deleted=False, is_active=True, is_private=False)
    courses = Course.objects.filter(ads_query)
    return courses[:21]

def last_ankets_for_russia():
    from love_posts.models import Anketa
    from django.db.models import Q

    ankets_query = Q(city__region__country__id=1, creator__is_blocked=False, is_deleted=False, is_active=True)
    ankets = Anketa.objects.filter(ankets_query)
    return ankets[:21]

def get_first_location(request, user):
    import json, requests
    from users.model.profile import OneUserLocation
    from users.model.profile import IPUser

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    olds_ip = IPUser.objects.create(user=user)
    response = requests.get(url= "http://api.sypexgeo.net/8Dbm8/json/" + ip)
    data = response.json()
    loc = OneUserLocation.objects.create(user=user)
    sity = data['city']
    region = data['region']
    country = data['country']
    loc.city_ru = sity['name_ru']
    loc.city_en = sity['name_en']
    loc.city_lat = sity['lat']
    loc.city_lon = sity['lon']
    loc.region_ru = region['name_ru']
    loc.region_en = region['name_en']
    loc.country_ru = country['name_ru']
    loc.country_en = country['name_en']
    loc.phone = country['phone']
    olds_ip.ip_1 = ip
    olds_ip.save()
    loc.save()


def get_location(request):
    import json, requests

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
        olds_ip = request.user.user_ip
    except:
        from users.model.profile import IPUser
        olds_ip = IPUser.objects.create(user=request.user)

    if not olds_ip.ip_1:
        response = requests.get(url= "http://api.sypexgeo.net/8Dbm8/json/" + ip)
        data = response.json()
        try:
            loc = request.user.user_location
        except:
            from users.model.profile import OneUserLocation
            loc = OneUserLocation.objects.create(user=request.user)
        sity = data['city']
        region = data['region']
        country = data['country']
        loc.city_ru = sity['name_ru']
        loc.city_en = sity['name_en']
        loc.city_lat = sity['lat']
        loc.city_lon = sity['lon']
        loc.region_ru = region['name_ru']
        loc.region_en = region['name_en']
        loc.country_ru = country['name_ru']
        loc.country_en = country['name_en']
        loc.phone = country['phone']
        olds_ip.ip_1 = ip
        olds_ip.save()
        loc.save()
    elif not olds_ip.ip_2 and olds_ip.ip_3 != ip and olds_ip.ip_2 != ip and olds_ip.ip_1 != ip:
        response = requests.get(url= "http://api.sypexgeo.net/8Dbm8/json/" + ip)
        data = response.json()
        try:
            loc = request.user.user_location_2
        except:
            from users.model.profile import TwoUserLocation
            loc = TwoUserLocation.objects.create(user=request.user)
        sity = data['city']
        region = data['region']
        country = data['country']
        loc.city_ru = sity['name_ru']
        loc.city_en = sity['name_en']
        loc.city_lat = sity['lat']
        loc.city_lon = sity['lon']
        loc.region_ru = region['name_ru']
        loc.region_en = region['name_en']
        loc.country_ru = country['name_ru']
        loc.country_en = country['name_en']
        loc.phone = country['phone']
        olds_ip.ip_2 = ip
        olds_ip.save()
        loc.save()
    elif not olds_ip.ip_3 and olds_ip.ip_3 != ip and olds_ip.ip_2 != ip and olds_ip.ip_1 != ip:
        response = requests.get(url= "http://api.sypexgeo.net/8Dbm8/json/" + ip)
        data = response.json()
        try:
            loc = request.user.user_location_3
        except:
            from users.model.profile import ThreeUserLocation
            loc = ThreeUserLocation.objects.create(user=request.user)
        sity = data['city']
        region = data['region']
        country = data['country']
        loc.city_ru = sity['name_ru']
        loc.city_en = sity['name_en']
        loc.city_lat = sity['lat']
        loc.city_lon = sity['lon']
        loc.region_ru = region['name_ru']
        loc.region_en = region['name_en']
        loc.country_ru = country['name_ru']
        loc.country_en = country['name_en']
        loc.phone = country['phone']
        olds_ip.ip_3 = ip
        olds_ip.save()
        loc.save()
    elif olds_ip.ip_3 and olds_ip.ip_3 != ip and olds_ip.ip_2 != ip and olds_ip.ip_1 != ip:
        response = requests.get(url= "http://api.sypexgeo.net/8Dbm8/json/" + ip)
        data = response.json()
        sity = data['city']
        region = data['region']
        country = data['country']
        loc.city_ru = sity['name_ru']
        loc.city_en = sity['name_en']
        loc.region_ru = region['name_ru']
        loc.region_en = region['name_en']
        loc.country_ru = country['name_ru']
        loc.country_en = country['name_en']
        loc.phone = country['phone']
        olds_ip.ip_1 = ip
        olds_ip.save()
        loc.save()

    else:
        pass
