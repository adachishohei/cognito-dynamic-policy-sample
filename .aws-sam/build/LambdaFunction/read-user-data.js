const AWS = require('aws-sdk')
const s3 = new AWS.S3()
const sts = new AWS.STS();

var params = {
    Policy: "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"dynamodb:GetItem\",\"dynamodb:BatchGetItem\",\"dynamodb:Query\"],\"Resource\":[\"arn:aws:dynamodb:ap-northeast-1:261812635110:table/Sample\"],\"Condition\":{\"ForAllValues:StringEquals\":{\"dynamodb:LeadingKeys\":[\"User1\"]}}}]}",
    RoleArn: "arn:aws:iam::261812635110:role/userAssumeRole",
    RoleSessionName: "userAssumeRoleSession",
};

exports.handler = function(event, context, callback) {
    sts.assumeRole(params, function (err, data){
        if(err) console.log(err, err.stack);
        else console.log(data);
    })
    return "OK"
}