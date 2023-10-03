#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BedrockStack } from '../lib/bedrock-stack';

const app = new cdk.App();

const bedrockStack= new BedrockStack(app, 'BedrockStack', {
});