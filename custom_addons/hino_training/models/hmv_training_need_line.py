# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingNeedCompanyTab(models.Model):
    _name = 'hmv.training.need.company'
    _description = 'Training Courses Provided By Company Tab'
    # _sql_constraints = [
    #     ('unique_employee_company', 
    #      'UNIQUE(training_need_id, employee_id)',
    #      'This employee is already registered in Company Training tab!')
    # ]

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    
    # Cái này là để lấy ra danh sách company course tương ứng với training brochure
    training_brochure_line_id = fields.Many2many(
        'hmv.training.brochure.line',
        'training_need_company_brochure_rel',  # Tên bảng trung gian
        'training_need_company_id',  # Khóa ngoại trỏ về model này
        'brochure_line_id',  # Khóa ngoại trỏ về model hmv.training.brochure.line 
        string='Courses',
        required=True,
        domain="[('training_brochure_id_company', '=', parent.training_brochure_id)]"
    )
    
    
    @api.constrains('employee_id', 'training_need_id')
    def _check_unique_employee(self):
        for record in self:
            duplicate = self.search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id)
            ])
            
            if duplicate:
                raise ValidationError(
                    f'Employee {record.employee_id.name} has already been added to Company Training tab!'
                )
    

    @api.constrains('employee_id', 'training_brochure_line_id')
    def _check_max_courses(self):
        for record in self:
            if len(record.training_brochure_line_id) > 2:
                raise ValidationError(
                    f'Employee {record.employee_id.name} cannot register for more than 2 company training courses!'
                )
        


# Hàm kiểm tra tổng số khóa học trên tất cả các tab
    @api.constrains('employee_id', 'training_brochure_line_id')
    def _check_max_courses_total(self):
        for record in self:
            if not record.employee_id:
                continue

            # Kiểm tra xem người dùng hiện tại có phải là nhân viên HR không
            current_user_employee = self.env.user.employee_id
            is_hr_employee = current_user_employee and current_user_employee.department_id.name == 'HR'

            # Nếu là HR, bỏ qua kiểm tra
            if is_hr_employee:
                continue

            # Đếm số khóa học trong tab Company
            company_courses = len(record.training_brochure_line_id)

            # Đếm số khóa học trong tab Factory
            factory_tab = self.env['hmv.training.need.factory'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            factory_courses = len(factory_tab.training_brochure_line_id) if factory_tab else 0

            # Đếm số khóa học trong tab Other
            other_tab = self.env['hmv.training.need.other'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            other_courses = len(other_tab.training_brochure_line_id) if other_tab else 0

            # Tổng số khóa học
            total_courses = company_courses + factory_courses + other_courses

            if total_courses > 2:
                raise ValidationError(
                    f'Employee {record.employee_id.name} can not register above 2 courses!'
                )   




class TrainingNeedFactoryTab(models.Model):
    _name = 'hmv.training.need.factory'
    _description = 'Factory Training Tab'
    # _sql_constraints = [
    #     ('unique_employee_factory',
    #      'UNIQUE(training_need_id, employee_id)', 
    #      'This employee is already registered in Factory Training tab!')
    # ]

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    # For TrainingNeedFactoryTab model
    training_brochure_line_id = fields.Many2many(
        'hmv.training.brochure.line',      # Model đích
        'factory_training_need_brochure_rel',   # Changed: Unique relation table name
        'factory_need_id',         # Changed: Unique column name
        'brochure_line_id',       # Changed: Unique column name
        string='Factory Training Courses',
        required=True,
        domain="[('training_brochure_id_factory', '=', parent.training_brochure_id)]",
        help="Selected training courses from Training brochure"
    )
    
    
                
    @api.constrains('employee_id', 'training_need_id')
    def _check_unique_employee(self):
        for record in self:
            # Tìm kiếm record trùng
            duplicate = self.search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id)
            ])
            
            if duplicate:
                raise ValidationError(
                    f'Employee {record.employee_id.name} is already registered in Factory Training tab!'
                )

# Hàm kiểm tra tổng số khóa học trên tất cả các tab
    @api.constrains('employee_id', 'training_brochure_line_id')
    def _check_max_courses_total(self):
        for record in self:
            if not record.employee_id:
                continue

            # Kiểm tra xem người dùng hiện tại có phải là nhân viên HR không
            current_user_employee = self.env.user.employee_id
            is_hr_employee = current_user_employee and current_user_employee.department_id.name == 'HR'

            # Nếu là HR, bỏ qua kiểm tra
            if is_hr_employee:
                continue

            # Đếm số khóa học trong tab Factory
            factory_courses = len(record.training_brochure_line_id)

            # Đếm số khóa học trong tab Company
            company_tab = self.env['hmv.training.need.company'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            company_courses = len(company_tab.training_brochure_line_id) if company_tab else 0

            # Đếm số khóa học trong tab Other
            other_tab = self.env['hmv.training.need.other'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            other_courses = len(other_tab.training_brochure_line_id) if other_tab else 0

            # Tổng số khóa học
            total_courses = factory_courses + company_courses + other_courses

            if total_courses > 2:
                raise ValidationError(
                    f'Employee {record.employee_id.name} can not register above 2 courses!'
                )
                
                
                







class TrainingNeedOtherTab(models.Model):
    _name = 'hmv.training.need.other'
    _description = 'Other Training Tab'
    # _sql_constraints = [
    #     ('unique_employee_other',
    #      'UNIQUE(training_need_id, employee_id)',
    #      'This employee is already registered in Other Training tab!')
    # ]

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    # For TrainingNeedOtherTab model 
    training_brochure_line_id = fields.Many2many(
        'hmv.training.brochure.line',      # Model đích
        'other_training_brochure_plan_rel',   # Changed: Unique relation table name
        'other_need_id',         # Changed: Unique column name
        'brochure_line_id',       # Changed: Unique column name
        string='Other Training Courses',
        required=True,
        domain="[('training_brochure_id_other', '=', parent.training_brochure_id)]",
        help="Selected training courses from Training brochure"
    )
    
    
    
                
    @api.constrains('employee_id', 'training_need_id')
    def _check_unique_employee(self):
        for record in self:
            # Tìm kiếm record trùng
            duplicate = self.search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id)
            ])
            
            if duplicate:
                raise ValidationError(
                    f'Employee {record.employee_id.name} is already registered in Other Training tab!'
                )




# Hàm kiểm tra tổng số khóa học trên tất cả các tab
    @api.onchange('employee_id', 'training_brochure_line_id')
    def _check_max_courses_total(self):
        for record in self:
            if not record.employee_id:
                continue

            # Kiểm tra xem người dùng hiện tại có phải là nhân viên HR không
            current_user_employee = self.env.user.employee_id
            is_hr_employee = current_user_employee and current_user_employee.department_id.name == 'HR'

            # Nếu là HR, bỏ qua kiểm tra
            if is_hr_employee:
                continue

            # Đếm số khóa học trong tab Other
            other_courses = len(record.training_brochure_line_id)

            # Đếm số khóa học trong tab Company
            company_tab = self.env['hmv.training.need.company'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            company_courses = len(company_tab.training_brochure_line_id) if company_tab else 0

            # Đếm số khóa học trong tab Factory
            factory_tab = self.env['hmv.training.need.factory'].search([
                ('training_need_id', '=', record.training_need_id.id),
                ('employee_id', '=', record.employee_id.id)
            ])
            factory_courses = len(factory_tab.training_brochure_line_id) if factory_tab else 0

            # Tổng số khóa học
            total_courses = other_courses + company_courses + factory_courses

            if total_courses > 2:
                raise ValidationError(
                    f'Employee {record.employee_id.name} can not register above 2 courses!'
                )






class TrainingNeedApprovalHistory(models.Model):
    _name = 'hmv.training.need.approval'
    _description = 'Approval History Tab'
    _order = 'id asc'

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Approver',
        help="Tên người trong luồng phê duyệt"
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='Position',
        related='employee_id.job_id',
        store=True,
        help="Vị trí của người trong luồng phê duyệt"
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        help="Phòng ban của người trong luồng phê duyệt"
    )
    
    status = fields.Selection([
        ('waiting', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='waiting',
       help="Waiting to approve: Chưa duyệt\nApproved: Đã duyệt\nRejected: Từ chối")
    
    comment = fields.Text(
        string='Comment',
        help="Lưu lại comment của approver khi approve/rejected"
    )