import os
import boto3
import json

from dotenv import load_dotenv
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

load_dotenv()
iam_client = boto3.client("iam")
role = iam_client.get_role(RoleName="GPU_LLM_Inference")["Role"]["Arn"]


def deploy_sagemaker_model(model_name=None):
    _model_name = model_name or "mncai/mistral-7b-v5"

    # Hub model configuration <https://huggingface.co/models>
    hub = {
        "HF_MODEL_ID": _model_name,  # model_id from hf.co/models
        "SM_NUM_GPUS": json.dumps(1),
    }

    # create Hugging Face Model Class
    huggingface_model = HuggingFaceModel(
        image_uri=get_huggingface_llm_image_uri("huggingface", version="1.1.0"),
        env=hub,
        role=role,
    )

    # deploy model to SageMaker Inference
    predictor = huggingface_model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.xlarge",  # "ml.g5.2xlarge"
        container_startup_health_check_timeout=300,
    )

    return predictor


# # send request
# resp = predictor.predict(
#     {
#         "inputs": "My name is Julien and I like to",
#     }
# )

# print(resp)

# # delete
# predictor.delete_endpoint()
