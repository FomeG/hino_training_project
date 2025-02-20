
# NOTE:
- ODOO 17 DOES NOT HAVE ATTRS AND STATES, USE VISIBLE OR INVISIBLE INSTEAD


# WORKFLOW:
1. Tạo Phiếu Training Brochure
    -   Bộ phận HR tạo các khóa học dự kiến sẽ tổ chức trong năm để các phòng ban có thể đăng ký tham gia khóa học
    -	Sau khi nhập đầy đủ thông tin về nội dung lập khóa học dự kiến, hệ thống sẽ hiển thị ra nút “Update Course”, màn hình sẽ hiển thị ra những khóa học có Status “Active”, “In Progress” trong Training Course, người dùng có thể  tích chọn để thực hiện chèn vào Training Brochure của năm tiếp theo

2. Tạo phiếu Training Plan
    -	Phiếu training plan được phòng nhân sự tạo kế hoạch học tập dự kiến trong năm, mỗi năm tạo một lần và không cho nhập trùng năm, để các phòng ban có thể đăng ký được
    -	Cách vào phiếu: Home – Training – Training Plan

3. Tạo phiếu Training Need
    -	Sau khi đã có Training Plan, các bộ phận tạo Phiếu Training Need để đăng ký số lượng học viên tham gia khóa học, phục vụ cho việc bộ phận mua hàng đi ký hợp đồng mua khóa học với các nhà cung cấp
    -	Giới hạn mỗi học viên chỉ được đăng ký tối đa 2 khóa học, Nhân viên phòng HR có quyền đăng ký thêm khóa học cho học viên nếu có phát sinh.
    -	Mỗi phòng ban chỉ được tạo một nhu cầu học tập trong 1 năm.


    3.2.	Gửi email thông báo
    Giải pháp: Thêm button Send Email, sau khi manager lập và assign cho nhân viên, hệ thống gửi thông báo cho nhân viên được assign hoàn thành yêu cầu phiếu Training Need
    - Sau khi thêm mới phiếu và có assign cho nhân viên thì hệ thống tự động gửi email thông báo, thiết kế thêm nút send email ở ngoài màn hình nếu manager cần gửi thông báo lại.

