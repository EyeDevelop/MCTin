import json
import hashlib
import os
from wsgiref.util import FileWrapper

from django.http import JsonResponse, StreamingHttpResponse, Http404
from django.shortcuts import redirect

from Server.settings import BASE_DIR

# region Error Messages

INVALID_OPERATION = JsonResponse({"error": "400", "message": "Illegal operation!"}, json_dumps_params={"indent": 4})
MODPACK_NOT_ENABLED = JsonResponse({"error": "403", "message": "Modpack is not enabled!"}, json_dumps_params={"indent": 4})
MODPACK_NOT_FOUND = JsonResponse({"error": "404", "message": "Modpack not found!"}, json_dumps_params={"indent": 4})
MODPACK_JAR_NOT_FOUND = JsonResponse({"error": "404", "message": "Requested installed is not available!"}, json_dumps_params={"indent": 4})
MOD_NOT_ENABLED = JsonResponse({"error": "403", "message": "Mod is not enabled!"}, json_dumps_params={"indent": 4})
MOD_NOT_FOUND = JsonResponse({"error": "404", "message": "Mod not found!"}, json_dumps_params={"indent": 4})
CHECKSUM_NOT_POSSIBLE = JsonResponse({"error": "501", "message": "Cannot calculate checksum on remote mods."}, json_dumps_params={"indent": 4})

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
    if "getmodpacks" in request.GET.keys():
        modpacks = {}
        for mp_dirname in [x for x in os.listdir(os.path.join(BASE_DIR, "data/modpacks/")) if not os.path.isfile(x)]:
            if "modpack.json" in os.listdir(os.path.join(BASE_DIR, "data/modpacks/{}".format(mp_dirname))):
                with open(os.path.join(BASE_DIR, "data/modpacks/{}/modpack.json".format(mp_dirname))) as mp_fp:
                    modpack = json.load(mp_fp)

                    if modpack["enabled"] != "yes":
                        continue

                    modpacks[mp_dirname] = {"name": modpack["name"], "version": modpack["version"], "description": modpack["description"]}

        return JsonResponse(modpacks, json_dumps_params={"indent": 4})

    elif "modpack" in request.GET.keys():
        modpack = get_modpack(request.GET.get("modpack"))
        if not modpack:
            return MODPACK_NOT_FOUND

        if modpack["enabled"] != "yes":
            return MODPACK_NOT_ENABLED

        if "getmods" in request.GET.keys():
            enabled_mods = {x: modpack["mods"][x] for x in modpack["mods"] if modpack["mods"][x]["enabled"] == "yes"}
            return JsonResponse(enabled_mods, json_dumps_params={"indent": 4})

        elif "getmod" in request.GET.keys():
            mod = get_mod(request.GET.get("getmod"), request.GET.get("modpack"))
            if not mod:
                return MOD_NOT_FOUND

            return JsonResponse(mod, json_dumps_params={"indent": 4})

        elif "downloadmod" in request.GET.keys():
            mod = get_mod(request.GET.get("downloadmod"), request.GET.get("modpack"))
            if not mod:
                return MOD_NOT_FOUND

            if mod["enabled"] != "yes":
                return MOD_NOT_ENABLED

            if "remote:" in mod["link"]:
                return redirect(mod["link"][7:])
            else:
                return redirect("/modpacks/{}/mods/{}".format(request.GET.get("modpack"), mod["link"]))

        elif "getchecksum" in request.GET.keys():
            mod = get_mod(request.GET.get("getchecksum"), request.GET.get("modpack"))

            if "remote:" in mod["link"]:
                return CHECKSUM_NOT_POSSIBLE

            h_sha256 = hashlib.sha256()
            with open(os.path.join(BASE_DIR, "data/modpacks/{}/mods/{}".format(request.GET.get("modpack"), mod["link"])), 'rb') as m_fp:
                h_sha256.update(m_fp.read())

            return JsonResponse({"checksum": h_sha256.hexdigest()}, json_dumps_params={"indent": 4})

        elif "getinstaller" in request.GET.keys():
            if not os.path.exists(os.path.join(BASE_DIR, "data/modpacks/{}/{}.{}".format(request.GET.get("modpack"), modpack["forge_installer"], request.GET.get("getinstaller")))):
                return MODPACK_JAR_NOT_FOUND
            return redirect("/modpacks/{}/{}.{}".format(request.GET.get("modpack"), modpack["forge_installer"], request.GET.get("getinstaller")))

        elif "getinstallerchecksum" in request.GET.keys():
            h_sha256 = hashlib.sha256()
            with open(os.path.join(BASE_DIR, "data/modpacks/{}/{}.{}".format(request.GET.get("modpack"), modpack["forge_installer"], request.GET.get("getinstallerchecksum"))), 'rb') as j_fp:
                h_sha256.update(j_fp.read())

            return JsonResponse({"checksum": h_sha256.hexdigest()}, json_dumps_params={"indent": 4})

        else:
            enabled_mods = {x: modpack["mods"][x] for x in modpack["mods"] if modpack["mods"][x]["enabled"] == "yes"}
            modpack["mods"] = enabled_mods
            return JsonResponse(modpack, json_dumps_params={"indent": 4})

    else:
        return INVALID_OPERATION


def serve(request, file):
    path = os.path.join(BASE_DIR, "data/modpacks/{}".format(file))

    if not os.path.exists(path):
        raise Http404("Jar file not found!")

    if not os.path.isfile(path):
        raise Http404("Jar file not found!")

    chunk_size = 8192
    m_fw = FileWrapper(open(path, 'rb'), chunk_size)
    response = StreamingHttpResponse(m_fw, content_type="application/octet-stream")
    response["Content-Length"] = os.path.getsize(path)
    response['Content-Disposition'] = "attachment; filename={}".format(os.path.basename(path))
    return response
