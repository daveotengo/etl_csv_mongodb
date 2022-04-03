from kanpai import Kanpai

add_item_param_validation = Kanpai.Object({
 "Datetime"    : Kanpai.String().trim().required("Param DateTime is required"),
 "amount": Kanpai.String().trim().required("Param amount is required"),
})

update_item_param_validation = Kanpai.Object({
 "Datetime"    : Kanpai.String().trim().required("Param DateTime is required"),
 "amount": Kanpai.String().trim().required("Param amount is required"),
})





























# "emailId" : Kanpai.Email().required(),
# "password": Kanpai.String().required("Please enter your password"),
# "confirmPassword" : Kanpai.String().required("Please re-enter your password")