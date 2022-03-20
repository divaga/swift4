# Smart Document Check
This is an API to identify PII document using Textract. This API is deployed through API Gateway and Lambda function which calls Textract endpoint. The deployment of this API uses AWS CDK as Infrastructure as a Code tool to ensure consistent, reliable, and repeatable infrastructure creation. There are a few prerequisites for using AWS CDK including Typescript and AWS CLI installation, so user has to ensure that those tools are also installed.

## Steps to deploy API
1. This API is deployed through CDK, please install AWS CDK and its pre-requisites
2. Create and deploy Lambda and API Gateway resource using AWS CDK in `cdk/` directory by running `npx cdk deploy`. See the instruction [below](#steps-to-install-aws-cdk) for more details
3. Upload identity documents and start getting result
  
  <br>
  
# AWS CDK
AWS CDK is a framework for defining cloud infrastructure in code and provisioning it through AWS CloudFormation [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html). To get started with AWS CDK, you can refer to this [CDK documentation](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html).

## Steps to install AWS CDK
1. Have AWS CLI installed and configure it with AWS credentials and AWS region. To install AWS CLI, please refer to this documentation [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. AWS CDK requires Typescript so install Typescript: `npm -g install typescript`
3. Install AWS CDK library: `npm -g install aws-cdk`

## How to deploy infrastructure in `cdk/` directory
1. Go to cdk directory: `cd cdk`
2. Install the necessary node modules: `npm i`
3. (*Optional*) Do a cdk synthetize to dry run: `npx cdk synth`
4. Once synthesis works, we can start to deploy using: `npx cdk deploy`

Note that `npx` command is used here to ensure CDK version specified by `package.json` is used instead of global CDK. This is to avoid possible version conflict between the local and global version of CDK. More information can be found in [NPX doc](https://nodejs.dev/learn/the-npx-nodejs-package-runner).
  
  <br>
  
# Todo
1. Create an image saving to S3 process
2. ~~Create a CDK to deploy API Gateway Resource~~
3. Create Lambda CDK to deploy Lambda Resource
4. Add GIF animation for clearer documentation