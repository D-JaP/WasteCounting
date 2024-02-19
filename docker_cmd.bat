aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com
docker build --rm --progress plain -t wastecounter_parkvic_api_v2 . 
@REM docker run -v C:\Users\dzung\.aws:/root/.aws -it --rm -p 9000:8080  wastecounter_lambda_s3
docker tag wastecounter_parkvic_api_v2:latest 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com/wastecounter_parkvic_api_v2:latest
aws ecr batch-delete-image --repository-name wastecounter_parkvic_api_v2 --image-ids imageTag=latest
docker push 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com/wastecounter_parkvic_api_v2:latest
aws lambda update-function-code --function-name parkvic-api-v2-single --image-uri 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com/wastecounter_parkvic_api_v2:latest
