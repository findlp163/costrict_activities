// 表单元素
const form = document.getElementById('team-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const successMessage = document.getElementById('success-message');
const toastContainer = document.getElementById('toast-container');
const addMemberBtn = document.getElementById('add-member-btn');
const membersContainer = document.getElementById('members-container');

const addTeacherBtn = document.getElementById('add-teacher-btn');
const advisorSection = document.getElementById('advisor-section');
const advisorContainer = document.getElementById('advisor-container');

let memberCount = 1; // 初始已有1个成员
let advisorCount = 0; // 初始没有指导老师

// 验证规则
const validationRules = {
    'team-name': {
        validate: (value) => value.trim().length > 0,
        message: '请填写团队名称'
    },
    'competition-track': {
        validate: (value) => value !== '',
        message: '请选择参赛赛道'
    },
    'project-name': {
        validate: (value) => value.trim().length > 0,
        message: '请填写作品名称'
    },
    'costrict-uid': {
        validate: (value) => value.trim().length > 0,
        message: '请填写CoStrict 用户ID'
    },
    'project-intro': {
        validate: (value) => {
            if (!value.trim()) return true; // 可选字段
            return value.length >= 200 && value.length <= 500;
        },
        message: '项目简介长度必须在200-500字之间'
    },
    'tech-solution': {
        validate: (value) => {
            if (!value.trim()) return true; // 可选字段
            return value.length >= 200 && value.length <= 500;
        },
        message: '技术方案长度必须在200-500字之间'
    },
    'goals-outlook': {
        validate: (value) => {
            if (!value.trim()) return true; // 可选字段
            return value.length >= 200 && value.length <= 500;
        },
        message: '目标与展望长度必须在200-500字之间'
    }
};

// 成员字段验证规则
const memberValidationRules = {
    name: {
        validate: (value) => value.trim().length >= 2,
        message: '姓名至少需要2个字符'
    },
    school: {
        validate: (value) => value.trim().length > 0,
        message: '请填写学校/单位'
    },
    department: {
        validate: (value) => value.trim().length > 0,
        message: '请填写学院/系别'
    },
    major_grade: {
        validate: (value) => value.trim().length > 0,
        message: '请填写专业与年级'
    },
    phone: {
        validate: (value) => {
            const phoneRegex = /^1[3-9]\d{9}$/;
            return phoneRegex.test(value);
        },
        message: '请输入有效的11位手机号'
    },
    email: {
        validate: (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(value);
        },
        message: '请输入有效的邮箱地址'
    },
    role: {
        validate: (value) => value.trim().length > 0,
        message: '请填写项目角色'
    }
};

// 指导老师字段验证规则
const advisorValidationRules = {
    name: {
        validate: (value) => value.trim().length >= 2,
        message: '姓名至少需要2个字符'
    },
    phone: {
        validate: (value) => {
            const phoneRegex = /^1[3-9]\d{9}$/;
            return phoneRegex.test(value);
        },
        message: '请输入有效的11位手机号'
    },
    email: {
        validate: (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(value);
        },
        message: '请输入有效的邮箱地址'
    },
    school: {
        validate: (value) => value.trim().length > 0,
        message: '请填写学校'
    },
    department: {
        validate: (value) => value.trim().length > 0,
        message: '请填写学院'
    }
};

// 实时验证
function validateField(fieldName, value) {
    const rule = validationRules[fieldName];
    if (!rule) return true;

    const isValid = rule.validate(value);
    const errorElement = document.getElementById(`${fieldName}-error`);
    
    if (errorElement) {
        if (!isValid) {
            errorElement.textContent = rule.message;
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }
    
    return isValid;
}

// 显示字段错误
function showFieldError(fieldName, message) {
    const errorElement = document.getElementById(`${fieldName}-error`);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

// 清除字段错误
function clearFieldError(fieldName) {
    const errorElement = document.getElementById(`${fieldName}-error`);
    if (errorElement) {
        errorElement.textContent = '';
    }
}

// 添加新成员
function addMember() {
    // 检查成员数量限制
    const currentMembers = document.querySelectorAll('.member-item').length;
    if (currentMembers >= 5) {
        showToast('最多只能添加5个成员', { type: 'error', title: '人数限制' });
        return;
    }
    
    memberCount++;
    const memberIndex = memberCount - 1;
    
    const memberItem = document.createElement('div');
    memberItem.className = 'member-item';
    memberItem.setAttribute('data-member-index', memberIndex);
    
    memberItem.innerHTML = `
        <div class="member-header">
            <h3>成员 ${memberCount} <button type="button" class="toggle-btn" data-index="${memberIndex}">展开</button> <span class="member-name-display" id="member-name-display-${memberIndex}"></span></h3>
            <div class="member-actions">
                <div class="member-captain">
                    <label>
                        <input type="checkbox" name="member_captain_${memberIndex}" class="captain-checkbox"> 队长
                    </label>
                </div>
                <div class="member-remove">
                    <button type="button" class="remove-member-btn" data-index="${memberIndex}">删除</button>
                </div>
            </div>
        </div>
        <div class="member-content" id="member-content-${memberIndex}">
            <div class="form-group">
            <label for="member-name-${memberIndex}" class="required">姓名</label>
            <input type="text" id="member-name-${memberIndex}" name="member_name_${memberIndex}" required
                   placeholder="请输入姓名">
            <span class="error-message" id="member-name-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-school-${memberIndex}" class="required">学校/单位</label>
            <input type="text" id="member-school-${memberIndex}" name="member_school_${memberIndex}" required
                   placeholder="请输入学校或单位名称">
            <span class="error-message" id="member-school-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-department-${memberIndex}" class="required">学院/系别</label>
            <input type="text" id="member-department-${memberIndex}" name="member_department_${memberIndex}" required
                   placeholder="请输入学院或系别">
            <span class="error-message" id="member-department-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-major-grade-${memberIndex}" class="required">专业与年级</label>
            <input type="text" id="member-major-grade-${memberIndex}" name="member_major_grade_${memberIndex}" required
                   placeholder="例如：计算机科学 大三">
            <span class="error-message" id="member-major-grade-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-phone-${memberIndex}" class="required">联系电话</label>
            <input type="tel" id="member-phone-${memberIndex}" name="member_phone_${memberIndex}" required
                   placeholder="请输入11位手机号" pattern="[0-9]{11}">
            <span class="error-message" id="member-phone-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-email-${memberIndex}" class="required">电子邮箱</label>
            <input type="email" id="member-email-${memberIndex}" name="member_email_${memberIndex}" required
                   placeholder="example@email.com">
            <span class="error-message" id="member-email-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-student-id-${memberIndex}">学号（可选）</label>
            <input type="text" id="member-student-id-${memberIndex}" name="member_student_id_${memberIndex}"
                   placeholder="用于身份验证，可选">
        </div>

        <div class="form-group">
            <label for="member-role-${memberIndex}" class="required">项目角色</label>
            <input type="text" id="member-role-${memberIndex}" name="member_role_${memberIndex}" required
                   placeholder="例如：前端开发、后端开发、算法、UI/UX设计、产品经理等">
            <span class="error-message" id="member-role-${memberIndex}-error"></span>
        </div>

        <div class="form-group">
            <label for="member-tech-stack-${memberIndex}">技术栈/擅长领域</label>
            <input type="text" id="member-tech-stack-${memberIndex}" name="member_tech_stack_${memberIndex}"
                   placeholder="例如：Python, React, Node.js, TensorFlow, Figma">
        </div>
        </div>
    `;
    
    membersContainer.appendChild(memberItem);
    
    // 添加删除成员的事件监听
    const removeBtn = memberItem.querySelector('.remove-member-btn');
    removeBtn.addEventListener('click', function() {
        removeMember(this.getAttribute('data-index'));
    });
    
    // 添加折叠/展开按钮的事件监听
    const toggleBtn = memberItem.querySelector('.toggle-btn');
    const memberContent = memberItem.querySelector('.member-content');
    toggleBtn.addEventListener('click', function() {
        const index = this.getAttribute('data-index');
        toggleMember(index);
    });
    
    // 新添加的成员默认展开
    memberContent.style.display = 'block';
    toggleBtn.textContent = '折叠';
    
    // 添加姓名输入监听，实时显示在标题中
    const nameInput = memberItem.querySelector(`#member-name-${memberIndex}`);
    const nameDisplay = memberItem.querySelector(`#member-name-display-${memberIndex}`);
    if (nameInput && nameDisplay) {
        nameInput.addEventListener('input', function() {
            const name = this.value.trim();
            if (name) {
                nameDisplay.textContent = `: ${name}`;
            } else {
                nameDisplay.textContent = '';
            }
        });
    }
    
    // 添加队长选择的事件监听
    const captainCheckbox = memberItem.querySelector('.captain-checkbox');
    const captainContainer = memberItem.querySelector('.member-captain');
    captainCheckbox.addEventListener('change', function() {
        if (this.checked) {
            // 取消其他成员的队长选择
            document.querySelectorAll('.captain-checkbox').forEach(checkbox => {
                if (checkbox !== this) {
                    checkbox.checked = false;
                    const container = checkbox.closest('.member-captain');
                    if (container) {
                        container.classList.remove('captain-selected');
                    }
                }
            });
            // 添加当前成员的队长样式
            captainContainer.classList.add('captain-selected');
        } else {
            // 移除当前成员的队长样式
            captainContainer.classList.remove('captain-selected');
        }
    });
    
    // 如果默认选中，确保样式正确应用
    if (captainCheckbox.checked) {
        captainContainer.classList.add('captain-selected');
    }
}

// 添加指导老师
function addAdvisor() {
    // 如果已经有指导老师，显示提示并返回
    if (advisorCount >= 1) {
        showToast('只能添加一位指导老师', { type: 'error', title: '操作限制' });
        return;
    }
    
    // 显示指导老师部分
    advisorSection.style.display = 'block';
    advisorCount++;
    
    const advisorIndex = 0; // 只能有一个指导老师，所以索引始终为0
    
    const advisorItem = document.createElement('div');
    advisorItem.className = 'advisor-item';
    advisorItem.setAttribute('data-advisor-index', advisorIndex);
    
    advisorItem.innerHTML = `
        <div class="advisor-header">
            <h3>指导老师 <button type="button" class="toggle-btn-advisor" data-index="${advisorIndex}">展开</button> <span class="advisor-name-display" id="advisor-name-display-${advisorIndex}"></span></h3>
            <div class="advisor-actions">
                <div class="advisor-remove">
                    <button type="button" class="remove-advisor-btn" data-index="${advisorIndex}">删除</button>
                </div>
            </div>
        </div>
        <div class="advisor-content" id="advisor-content-${advisorIndex}">
            <div class="form-group">
                <label for="advisor-name-${advisorIndex}" class="required">姓名</label>
                <input type="text" id="advisor-name-${advisorIndex}" name="advisor_name_${advisorIndex}" required
                       placeholder="请输入指导老师姓名">
                <span class="error-message" id="advisor-name-${advisorIndex}-error"></span>
            </div>

            <div class="form-group">
                <label for="advisor-phone-${advisorIndex}" class="required">联系电话</label>
                <input type="tel" id="advisor-phone-${advisorIndex}" name="advisor_phone_${advisorIndex}" required
                       placeholder="请输入11位手机号" pattern="[0-9]{11}">
                <span class="error-message" id="advisor-phone-${advisorIndex}-error"></span>
            </div>

            <div class="form-group">
                <label for="advisor-email-${advisorIndex}" class="required">电子邮箱</label>
                <input type="email" id="advisor-email-${advisorIndex}" name="advisor_email_${advisorIndex}" required
                       placeholder="example@email.com">
                <span class="error-message" id="advisor-email-${advisorIndex}-error"></span>
            </div>

            <div class="form-group">
                <label for="advisor-school-${advisorIndex}" class="required">学校</label>
                <input type="text" id="advisor-school-${advisorIndex}" name="advisor_school_${advisorIndex}" required
                       placeholder="请输入学校名称">
                <span class="error-message" id="advisor-school-${advisorIndex}-error"></span>
            </div>

            <div class="form-group">
                <label for="advisor-department-${advisorIndex}" class="required">学院</label>
                <input type="text" id="advisor-department-${advisorIndex}" name="advisor_department_${advisorIndex}" required
                       placeholder="请输入学院名称">
                <span class="error-message" id="advisor-department-${advisorIndex}-error"></span>
            </div>

            <div class="form-group">
                <label for="advisor-intro-${advisorIndex}">简介（500字以内）</label>
                <textarea id="advisor-intro-${advisorIndex}" name="advisor_intro_${advisorIndex}" rows="4"
                          placeholder="请输入指导老师简介" maxlength="500"></textarea>
                <span class="error-message" id="advisor-intro-${advisorIndex}-error"></span>
            </div>
        </div>
    `;
    
    advisorContainer.appendChild(advisorItem);
    
    // 添加删除指导老师的事件监听
    const removeBtn = advisorItem.querySelector('.remove-advisor-btn');
    removeBtn.addEventListener('click', function() {
        removeAdvisor(this.getAttribute('data-index'));
    });
    
    // 添加折叠/展开按钮的事件监听
    const toggleBtn = advisorItem.querySelector('.toggle-btn-advisor');
    const advisorContent = advisorItem.querySelector('.advisor-content');
    toggleBtn.addEventListener('click', function() {
        const index = this.getAttribute('data-index');
        toggleAdvisor(index);
    });
    
    // 新添加的指导老师默认展开
    advisorContent.style.display = 'block';
    toggleBtn.textContent = '折叠';
    
    // 添加姓名输入监听，实时显示在标题中
    const nameInput = advisorItem.querySelector(`#advisor-name-${advisorIndex}`);
    const nameDisplay = advisorItem.querySelector(`#advisor-name-display-${advisorIndex}`);
    if (nameInput && nameDisplay) {
        nameInput.addEventListener('input', function() {
            const name = this.value.trim();
            if (name) {
                nameDisplay.textContent = `: ${name}`;
            } else {
                nameDisplay.textContent = '';
            }
        });
    }
}

// 折叠/展开指导老师内容
function toggleAdvisor(index) {
    const advisorContent = document.getElementById(`advisor-content-${index}`);
    const toggleBtn = document.querySelector(`.toggle-btn-advisor[data-index="${index}"]`);
    
    if (advisorContent.style.display === 'none') {
        advisorContent.style.display = 'block';
        toggleBtn.textContent = '折叠';
    } else {
        advisorContent.style.display = 'none';
        toggleBtn.textContent = '展开';
    }
}

// 删除指导老师
function removeAdvisor(index) {
    const advisorItem = document.querySelector(`.advisor-item[data-advisor-index="${index}"]`);
    if (advisorItem) {
        advisorItem.remove();
        advisorCount = 0;
        
        // 隐藏整个部分
        advisorSection.style.display = 'none';
    }
}

// 折叠/展开成员内容
function toggleMember(index) {
    const memberContent = document.getElementById(`member-content-${index}`);
    const toggleBtn = document.querySelector(`.toggle-btn[data-index="${index}"]`);
    
    if (memberContent.style.display === 'none') {
        memberContent.style.display = 'block';
        toggleBtn.textContent = '折叠';
    } else {
        memberContent.style.display = 'none';
        toggleBtn.textContent = '展开';
    }
}

// 删除成员
function removeMember(index) {
    if (memberCount <= 1) {
        showToast('至少需要保留一个成员', { type: 'error', title: '无法删除' });
        return;
    }
    
    const memberItem = document.querySelector(`.member-item[data-member-index="${index}"]`);
    if (memberItem) {
        memberItem.remove();
        // 重新编号成员标题
        const memberItems = document.querySelectorAll('.member-item');
        memberItems.forEach((item, i) => {
            const title = item.querySelector('.member-header h3');
            if (title) {
                title.textContent = `成员 ${i + 1}`;
            }
        });
        memberCount--;
    }
}

// 验证单个成员信息
function validateMember(memberIndex) {
    let isValid = true;
    const prefix = `member-`;
    
    // 首先检查成员元素是否存在
    const memberElement = document.getElementById(`member-name-${memberIndex}`);
    if (!memberElement) {
        console.warn(`成员元素不存在: ${memberIndex}`);
        return true; // 如果元素不存在，跳过验证
    }
    
    Object.keys(memberValidationRules).forEach(field => {
        const fieldElement = document.getElementById(`${prefix}${field}-${memberIndex}`);
        if (fieldElement) {
            const fieldValue = fieldElement.value.trim();
            const rule = memberValidationRules[field];
            
            if (!rule.validate(fieldValue)) {
                showFieldError(`${prefix}${field}-${memberIndex}`, rule.message);
                isValid = false;
            } else {
                clearFieldError(`${prefix}${field}-${memberIndex}`);
            }
        }
    });
    
    return isValid;
}

// 验证单个指导老师信息
function validateAdvisor(advisorIndex) {
    let isValid = true;
    const prefix = `advisor-`;
    
    // 首先检查指导老师元素是否存在
    const advisorElement = document.getElementById(`advisor-name-${advisorIndex}`);
    if (!advisorElement) {
        console.warn(`指导老师元素不存在: ${advisorIndex}`);
        return true; // 如果元素不存在，跳过验证
    }
    
    Object.keys(advisorValidationRules).forEach(field => {
        const fieldElement = document.getElementById(`${prefix}${field}-${advisorIndex}`);
        if (fieldElement) {
            const fieldValue = fieldElement.value.trim();
            const rule = advisorValidationRules[field];
            
            if (!rule.validate(fieldValue)) {
                showFieldError(`${prefix}${field}-${advisorIndex}`, rule.message);
                isValid = false;
            } else {
                clearFieldError(`${prefix}${field}-${advisorIndex}`);
            }
        }
    });
    
    return isValid;
}

// 验证整个表单
function validateForm() {
    let isValid = true;
    
    // 验证团队信息
    Object.keys(validationRules).forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field) {
            const fieldValue = field.value.trim();
            if (!validateField(fieldName, fieldValue)) {
                isValid = false;
            }
        }
    });
    
    // 验证所有成员信息
    const memberItems = document.querySelectorAll('.member-item');
    let memberCount = 0;
    memberItems.forEach(item => {
        const memberIndex = item.getAttribute('data-member-index');
        // 确保只验证实际存在的成员
        if (document.getElementById(`member-name-${memberIndex}`)) {
            memberCount++;
            if (!validateMember(memberIndex)) {
                isValid = false;
            }
        }
    });
    
    // 检查是否至少有一个队长
    let hasCaptain = false;
    document.querySelectorAll('.captain-checkbox').forEach(checkbox => {
        if (checkbox.checked) {
            hasCaptain = true;
        }
    });
    
    if (!hasCaptain) {
        showToast('请指定一名队长', { type: 'error', title: '验证失败' });
        isValid = false;
    }
    
    // 验证所有指导老师信息（如果有）
    const advisorItems = document.querySelectorAll('.advisor-item');
    let advisorCount = 0;
    advisorItems.forEach(item => {
        const advisorIndex = item.getAttribute('data-advisor-index');
        // 确保只验证实际存在的指导老师
        if (document.getElementById(`advisor-name-${advisorIndex}`)) {
            advisorCount++;
            if (!validateAdvisor(advisorIndex)) {
                isValid = false;
            }
        }
    });
    
    // 确保成员和指导老师的总数不超过限制
    const totalMembers = memberCount + advisorCount;
    if (totalMembers > 6) {
        showToast('团队总人数（成员+指导老师）不能超过6人', { type: 'error', title: '人数限制' });
        isValid = false;
    }
    
    return isValid;
}

// 获取表单数据
function getFormData() {
    // 团队信息
    const teamInfo = {
        team_name: document.getElementById('team-name').value.trim(),
        competition_track: document.getElementById('competition-track').value,
        project_name: document.getElementById('project-name').value.trim(),
        repo_url: document.getElementById('repo-url').value.trim(),
        costrict_uid: document.getElementById('costrict-uid').value.trim(),
        project_intro: document.getElementById('project-intro').value.trim(),
        tech_solution: document.getElementById('tech-solution').value.trim(),
        goals_and_outlook: document.getElementById('goals-outlook').value.trim()
    };
    
    // 成员信息
    const members = [];
    const memberItems = document.querySelectorAll('.member-item');
    
    memberItems.forEach(item => {
        const memberIndex = item.getAttribute('data-member-index');
        const captainCheckbox = item.querySelector('.captain-checkbox');
        
        // 根据队长复选框状态确定成员类型
        let memberType = '队员';
        if (captainCheckbox && captainCheckbox.checked) {
            memberType = '队长';
        }
        
        members.push({
            name: document.getElementById(`member-name-${memberIndex}`).value.trim(),
            member_type: memberType,
            school: document.getElementById(`member-school-${memberIndex}`).value.trim(),
            department: document.getElementById(`member-department-${memberIndex}`).value.trim(),
            major_grade: document.getElementById(`member-major-grade-${memberIndex}`).value.trim(),
            phone: document.getElementById(`member-phone-${memberIndex}`).value.trim(),
            email: document.getElementById(`member-email-${memberIndex}`).value.trim(),
            student_id: document.getElementById(`member-student-id-${memberIndex}`).value.trim(),
            role: document.getElementById(`member-role-${memberIndex}`).value.trim(),
            tech_stack: document.getElementById(`member-tech-stack-${memberIndex}`).value.trim(),
            desc: ''
        });
    });
    
    // 指导老师信息
    const advisorItems = document.querySelectorAll('.advisor-item');
    
    advisorItems.forEach(item => {
        const advisorIndex = item.getAttribute('data-advisor-index');
        
        members.push({
            name: document.getElementById(`advisor-name-${advisorIndex}`).value.trim(),
            member_type: '指导老师',
            school: document.getElementById(`advisor-school-${advisorIndex}`).value.trim(),
            department: document.getElementById(`advisor-department-${advisorIndex}`).value.trim(),
            major_grade: '', // 指导老师没有专业年级字段
            phone: document.getElementById(`advisor-phone-${advisorIndex}`).value.trim(),
            email: document.getElementById(`advisor-email-${advisorIndex}`).value.trim(),
            student_id: '', // 指导老师没有学号字段
            role: '指导老师',
            tech_stack: '', // 指导老师没有技术栈字段
            desc: document.getElementById(`advisor-intro-${advisorIndex}`).value.trim() // 使用desc字段存储简介
        });
    });
    
    return {
        team_info: teamInfo,
        members: members
    };
}

// 显示加载状态
function showLoading() {
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
}

// 隐藏加载状态
function hideLoading() {
    submitBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoader.style.display = 'none';
}

// 轻量级 Toast 通知（info/success/error）
function showToast(message, { type = 'info', title = '', duration = 3000 } = {}) {
    if (!toastContainer) return alert(message);

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'status');

    const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    icon.setAttribute('viewBox', '0 0 24 24');
    icon.setAttribute('fill', 'none');
    icon.setAttribute('stroke', 'currentColor');
    icon.classList.add('toast-icon');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    path.setAttribute('stroke-width', '2');

    if (type === 'success') {
        path.setAttribute('d', 'M5 13l4 4L19 7');
    } else if (type === 'error') {
        path.setAttribute('d', 'M6 18L18 6M6 6l12 12');
    } else {
        path.setAttribute('d', 'M13 16h-1v-4h-1m1-4h.01M12 19a7 7 0 110-14 7 7 0 010 14z');
    }
    icon.appendChild(path);

    const content = document.createElement('div');
    content.className = 'toast-content';
    if (title) {
        const titleEl = document.createElement('div');
        titleEl.className = 'toast-title';
        titleEl.textContent = title;
        content.appendChild(titleEl);
    }
    const msgEl = document.createElement('div');
    msgEl.className = 'toast-message';
    msgEl.textContent = message;
    content.appendChild(msgEl);

    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.setAttribute('aria-label', '关闭通知');
    closeBtn.innerHTML = '✕';
    closeBtn.addEventListener('click', () => removeToast(toast));

    toast.appendChild(icon);
    toast.appendChild(content);
    toast.appendChild(closeBtn);
    toastContainer.appendChild(toast);

    let hideTimer = null;
    const startTimer = () => {
        if (duration > 0) hideTimer = setTimeout(() => removeToast(toast), duration);
    };
    const clearTimer = () => { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } };
    startTimer();
    toast.addEventListener('mouseenter', clearTimer);
    toast.addEventListener('mouseleave', startTimer);

    function removeToast(el) {
        el.style.animation = 'toast-out 180ms ease-in forwards';
        setTimeout(() => {
            if (el.parentNode) el.parentNode.removeChild(el);
        }, 180);
    }
}

// 显示成功消息
function showSuccess() {
    form.style.display = 'none';
    successMessage.style.display = 'block';
    successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 提交表单
async function submitForm(event) {
    event.preventDefault();
    
    // 清除之前的错误
    Object.keys(validationRules).forEach(key => clearFieldError(key));
    
    // 清除成员字段错误
    const memberErrorElements = document.querySelectorAll('[id$="-error"]');
    memberErrorElements.forEach(el => {
        if (el.id.includes('member-') || el.id.includes('advisor-')) {
            el.textContent = '';
        }
    });
    
    // 校验是否勾选同意条款（若存在）
    const agree = document.getElementById('agree');
    if (agree && !agree.checked) {
        showToast('请先勾选同意"报名须知"。', { type: 'error', title: '未同意条款' });
        return;
    }
    
    // 验证表单
    if (!validateForm()) {
        // 滚动到第一个错误字段
        const firstError = document.querySelector('.error-message:not(:empty)');
        if (firstError) {
            firstError.closest('.form-group').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
        return;
    }
    
    // 获取表单数据
    const formData = getFormData();
    
    // 显示加载状态
    showLoading();
    
    try {
        // 发送到后端 API
        const response = await fetch('/api/team/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || '提交失败，请稍后重试');
        }
        
        const result = await response.json();
        
        // 模拟延迟（实际开发中可以移除）
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 显示成功消息
        showSuccess();
        
        // 可选：重置表单
        // form.reset();
        
    } catch (error) {
        console.error('提交错误:', error);
        showToast('提交失败：' + error.message, { type: 'error', title: '提交失败' });

        // 离线或无后端时：在控制台显示数据并模拟成功
        if (!navigator.onLine) {
            console.log('团队数据:', formData);
            showToast('离线状态，已模拟成功提交。', { type: 'success', title: '离线模拟' });
            setTimeout(() => { showSuccess(); }, 1000);
        }
    } finally {
        hideLoading();
    }
}

// 实时验证（输入时）
const fieldsToValidate = ['team-name', 'competition-track', 'project-name', 'costrict-uid', 'project-intro', 'tech-solution', 'goals-outlook'];
fieldsToValidate.forEach(fieldName => {
    const field = document.getElementById(fieldName);
    if (field) {
        field.addEventListener('blur', function() {
            validateField(fieldName, this.value);
        });
        
        field.addEventListener('input', function() {
            // 输入时清除错误（如果已经有效）
            if (validateField(fieldName, this.value)) {
                clearFieldError(fieldName);
            }
        });
    }
});

// 表单提交事件
form.addEventListener('submit', submitForm);

// 添加成员按钮事件
if (addMemberBtn) {
    addMemberBtn.addEventListener('click', addMember);
}

// 添加指导老师按钮事件
if (addTeacherBtn) {
    addTeacherBtn.addEventListener('click', addAdvisor);
}

// 初始队长选择事件
const initialCaptainCheckbox = document.querySelector('.captain-checkbox');
if (initialCaptainCheckbox) {
    const captainContainer = initialCaptainCheckbox.closest('.member-captain');
    initialCaptainCheckbox.addEventListener('change', function() {
        if (this.checked) {
            // 取消其他成员的队长选择
            document.querySelectorAll('.captain-checkbox').forEach(checkbox => {
                if (checkbox !== this) {
                    checkbox.checked = false;
                    const container = checkbox.closest('.member-captain');
                    if (container) {
                        container.classList.remove('captain-selected');
                    }
                }
            });
            // 添加当前成员的队长样式
            captainContainer.classList.add('captain-selected');
        } else {
            // 移除当前成员的队长样式
            captainContainer.classList.remove('captain-selected');
        }
    });
    
    // 确保初始状态样式正确
    if (initialCaptainCheckbox.checked) {
        captainContainer.classList.add('captain-selected');
    }
}

// 获取并显示报名截止时间
async function fetchAndDisplayDeadline() {
    try {
        const response = await fetch('/api/config?config_key=DEADLINE');
        
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.data) {
                const deadlineElement = document.getElementById('deadline-time');
                const deadlineNotice = document.getElementById('deadline-notice');
                
                if (deadlineElement && deadlineNotice) {
                    deadlineElement.textContent = result.data.value;
                    deadlineNotice.style.display = 'block';
                }
            }
        } else {
            console.log('未设置截止时间或获取失败');
        }
    } catch (error) {
        console.error('获取截止时间失败:', error);
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('团队表单页面已加载');
    
    // 获取并显示截止时间
    fetchAndDisplayDeadline();
    
    // 初始化成员折叠/展开功能
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        const index = btn.getAttribute('data-index');
        btn.addEventListener('click', function() {
            toggleMember(index);
        });
        
        // 默认折叠第一个成员以外的所有成员
        if (index > 0) {
            const memberContent = document.getElementById(`member-content-${index}`);
            if (memberContent) {
                memberContent.style.display = 'none';
                btn.textContent = '展开';
            }
        } else {
            // 第一个成员默认展开
            btn.textContent = '折叠';
        }
    });
    
    // 初始化成员验证和姓名显示
    const memberItems = document.querySelectorAll('.member-item');
    memberItems.forEach(item => {
        const memberIndex = item.getAttribute('data-member-index');
        
        // 添加姓名输入监听，实时显示在标题中
        const nameInput = item.querySelector(`#member-name-${memberIndex}`);
        const nameDisplay = item.querySelector(`#member-name-display-${memberIndex}`);
        if (nameInput && nameDisplay) {
            nameInput.addEventListener('input', function() {
                const name = this.value.trim();
                if (name) {
                    nameDisplay.textContent = `: ${name}`;
                } else {
                    nameDisplay.textContent = '';
                }
            });
        }
        
        Object.keys(memberValidationRules).forEach(field => {
            const fieldElement = document.getElementById(`member-${field}-${memberIndex}`);
            if (fieldElement) {
                fieldElement.addEventListener('blur', function() {
                    if (!memberValidationRules[field].validate(this.value.trim())) {
                        showFieldError(`member-${field}-${memberIndex}`, memberValidationRules[field].message);
                    } else {
                        clearFieldError(`member-${field}-${memberIndex}`);
                    }
                });
                
                fieldElement.addEventListener('input', function() {
                    if (memberValidationRules[field].validate(this.value.trim())) {
                        clearFieldError(`member-${field}-${memberIndex}`);
                    }
                });
            }
        });
    });
    
    // 初始化指导老师相关功能（只有在有指导老师时才执行）
    const toggleAdvisorBtns = document.querySelectorAll('.toggle-btn-advisor');
    toggleAdvisorBtns.forEach(btn => {
        const index = btn.getAttribute('data-index');
        btn.addEventListener('click', function() {
            toggleAdvisor(index);
        });
        
        // 默认展开第一个（也是唯一的）指导老师
        if (index == 0) {
            const advisorContent = document.getElementById(`advisor-content-${index}`);
            if (advisorContent) {
                advisorContent.style.display = 'block';
                btn.textContent = '折叠';
            }
        }
    });
    
    // 初始化指导老师验证和姓名显示
    const advisorItems = document.querySelectorAll('.advisor-item');
    advisorItems.forEach(item => {
        const advisorIndex = item.getAttribute('data-advisor-index');
        
        // 添加姓名输入监听，实时显示在标题中
        const nameInput = item.querySelector(`#advisor-name-${advisorIndex}`);
        const nameDisplay = item.querySelector(`#advisor-name-display-${advisorIndex}`);
        if (nameInput && nameDisplay) {
            nameInput.addEventListener('input', function() {
                const name = this.value.trim();
                if (name) {
                    nameDisplay.textContent = `: ${name}`;
                } else {
                    nameDisplay.textContent = '';
                }
            });
        }
        
        Object.keys(advisorValidationRules).forEach(field => {
            const fieldElement = document.getElementById(`advisor-${field}-${advisorIndex}`);
            if (fieldElement) {
                fieldElement.addEventListener('blur', function() {
                    if (!advisorValidationRules[field].validate(this.value.trim())) {
                        showFieldError(`advisor-${field}-${advisorIndex}`, advisorValidationRules[field].message);
                    } else {
                        clearFieldError(`advisor-${field}-${advisorIndex}`);
                    }
                });
                
                fieldElement.addEventListener('input', function() {
                    if (advisorValidationRules[field].validate(this.value.trim())) {
                        clearFieldError(`advisor-${field}-${advisorIndex}`);
                    }
                });
            }
        });
    });
});

