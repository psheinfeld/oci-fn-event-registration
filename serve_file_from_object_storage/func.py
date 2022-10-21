import io
import json
import logging
import oci
import time

from fdk import response

def read_object(ctx,config,signer,bucket_name,file_object_name):
    try:
        object_storage = oci.object_storage.ObjectStorageClient(config,
                                                                signer=signer)
        namespace = object_storage.get_namespace().data
        obj = object_storage.get_object(namespace, bucket_name,
                                        file_object_name)
        return response.Response(
            ctx,
            response_data=obj.data.content,
            headers={"Content-Type": obj.headers['Content-type']})
    except (Exception) as e:
        return response.Response(ctx,
                                 response_data="500 Server error : " + str(e),
                                 headers={"Content-Type": "text/plain"})

def handler(ctx, data: io.BytesIO = None):
    # #logging
    # log = logging.getLogger()
    # log_level = ctx.Config().get("logLevel")
    # log.setLevel("INFO" if not log_level else log_level)
    # log.debug("app log level : {}".format(log_level))

    #application config
    default_document = ctx.Config().get("default_document")
    bucket_name = ctx.Config().get("bucket_name")
    action_keyword = ctx.Config().get("action_keyword")
    registration_active = True if str(ctx.Config().get("registration_active")).lower() == "true" else False  #True/False
    show_config = True if str(ctx.Config().get("show_config")).lower() == "true" else False          #True/False

    #use file name
    RequestURL = str(ctx.RequestURL())
    file_object_name = RequestURL.replace(action_keyword, default_document, 1)
    file_object_name = file_object_name[1:] if file_object_name[
        0] == "/" else file_object_name

    #auth objects
    signer = oci.auth.signers.get_resource_principals_signer()
    config = {
        "tenancy": signer.tenancy_id,
        "region": signer.region,
        "RequestURL": RequestURL,
        "file_object_name": file_object_name,
        "request_method": ctx.Method(),
        "registration_active": registration_active,
        "show_config":show_config,
    }

    #debug options
    if show_config:
        return response.Response(ctx,
                             response_data=config,
                             headers={"Content-Type": "text"})

    if config["request_method"] == "GET":
        return read_object(ctx,config,signer,bucket_name,file_object_name)
    
    if config["request_method"] == "POST":
        body = ""
        try:
            body = json.loads(data.getvalue())
        except Exception as e:
            body = str(e)
        # name = body.get("name")
        return {"request":"success","data":body}