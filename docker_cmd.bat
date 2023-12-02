docker build --rm --progress plain -t wastecounter_lambda_s3 . 
@REM docker run -v C:\Users\dzung\.aws:/root/.aws -it --rm -p 9000:8080  wastecounter_lambda_s3
docker tag wastecounter_lambda_s3:latest 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com/wastecounter_parkvic:1.0.0
docker push 681503573350.dkr.ecr.ap-southeast-2.amazonaws.com/wastecounter_parkvic:1.0.0