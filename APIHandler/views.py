import json
import os

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import redirect

from Server.settings import BASE_DIR

# region Error Messages

INVALID_OPERATION = JsonResponse({"error": "400", "message": "Illegal operation!"}, json_dumps_params={"indent": 4})
MODPACK_NOT_ENABLED = JsonResponse({"error": "403", "message": "Modpack is not enabled!"}, json_dumps_params={"indent": 4})
MODPACK_NOT_FOUND = JsonResponse({"error": "404", "message": "Modpack not found!"}, json_dumps_params={"indent": 4})
MOD_NOT_ENABLED = JsonResponse({"error": "403", "message": "Mod is not enabled!"}, json_dumps_params={"indent": 4})
MOD_NOT_FOUND = JsonResponse({"error": "404", "message": "Mod not found!"}, json_dumps_params={"indent": 4})

# endregion


def check_modpack(modpack_name):
    if not os.path.exists(os.path.join(BASE_DIR, "data/modpacks/" + modpack_name + "/modpack.json")):
        return False

    return True


def get_modpack(modpack_name):
    if not check_modpack(modpack_name):
        return None

    with open(os.path.join(BASE_DIR, "data/modpacks/{}/modpack.json".format(modpack_name))) as mp_fp:
        modpack = json.load(mp_fp)

    return modpack


def check_mod(mod_name, modpack_name):
    modpack = get_modpack(modpack_name)

    if mod_name not in modpack["mods"].keys():
        return False

    return True


def get_mod(mod_name, modpack_name):
    if not check_mod(mod_name, modpack_name):
        return None

    modpack = get_modpack(modpack_name)
    mod = modpack["mods"][mod_name]

    return mod


# Create your views here.
def handle(request):
    if "modpack" in request.GET.keys():
        modpack = get_modpack(request.GET.get("modpack"))
        if not modpack:
            return MODPACK_NOT_FOUND

        if modpack["enabled"] != "yes":
            return MODPACK_NOT_ENABLED

        if "getmods" in request.GET.keys():
            return JsonResponse(modpack["mods"], json_dumps_params={"indent": 4})

        elif "getmodinfo" in request.GET.keys():
            mod = get_mod(request.GET.get("getmodinfo"), request.GET.get("modpack"))
            if not mod:
                return MOD_NOT_FOUND

            return JsonResponse(mod, json_dumps_params={"indent": 4})

        elif "getmod" in request.GET.keys():
            mod = get_mod(request.GET.get("getmod"), request.GET.get("modpack"))
            if not mod:
                return MOD_NOT_FOUND

            if mod["enabled"] != "yes":
                return MOD_NOT_ENABLED

            if "remote:" in mod["link"]:
                return redirect(mod["link"][7:])
            else:
                return redirect("/modpacks/{}/mods/{}".format(request.GET.get("modpack"), mod["link"]))

        elif "getjar" in request.GET.keys():
            return redirect("/modpacks/{}/{}".format(request.GET.get("modpack"), modpack["mc_jar"]))

        else:
            return JsonResponse(modpack, json_dumps_params={"indent": 4})

    else:
        return INVALID_OPERATION


def serve(request, file):
    path = os.path.join(BASE_DIR, "data/modpacks/{}".format(file))

    if not os.path.exists(path):
        raise Http404("Jar file not found!")

    if not os.path.isfile(path):
        raise Http404("Jar file not found!")

    with open(path, 'rb') as m_fp:
        return HttpResponse(m_fp, content_type="application/octet-stream")
