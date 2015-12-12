# watcher-elasticsearch
Watcher là một tool dùng để theo dõi và cảnh báo, cho phép bạn hành động dựa trên những thay đổi của dữ liệu trong elasticsearch

##Cấu hình
Cấu hình theo file config mẫu config.template
- eslaticsearch: địa chỉ của elasticsearch
- index: index trong elasticsearch muốn theo dõi
- interval: khoảng cách giữ 2 lần theo dõi, đơn vị là giây
- search: câu truy vấn, theo cú pháp của elasticsearch
- actions.gmail : Cấu hình cho action gửi mail
- action.logs: Cấu hình cho action send_to_logs

Chý ý: Cấu hình cho actions.gmail.msg và logs.format có thể sử dụng biến reponse (kết quả trả về của hàm Elasticsearch.search)

##Thêm action
- action là một function có duy nhất một tham số (là kết quả trả về của hàm Elasticsearch.search)
- Thêm action bằng cách gọi hàm: Wathcher.add_action(action_name)

##Thêm condition
- condition là một function có duy nhất một tham số (là kết quả trả về của hàm Elasticsearch.search) và trả về dạng boolean
- Thêm condition bằng cách gọi hàm: Wathcher.add_condition(action_name)

###Sử dụng
Khi gọi hàm Wathcer.run(), sau khoảng thời gian xác định watcher sẽ gửi truy vấn tới elasticsearch, sau đó thực hiệ các hàm condition nếu tất cả các hàm này đểu trả về True thì sẽ thực hiện các hàm actions
