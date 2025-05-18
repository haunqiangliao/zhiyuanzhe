import streamlit as st
import json
import os
from datetime import datetime, timedelta

class VolunteerActivityMatcher:
    def __init__(self):
        self.data_file = "volunteer_data.json"
        self.data = self._load_data()
        
    def _load_data(self):
        """加载或初始化数据文件"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                st.error("数据文件损坏，将创建新文件")
        return {"users": [], "activities": []}
    
    def _save_data(self):
        """保存数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_activity(self, name, category, location, date, time_range, description):
        """添加志愿活动"""
        activity = {
            "id": len(self.data["activities"]) + 1,
            "name": name,
            "category": category,
            "location": location,
            "date": date,
            "time_range": time_range,
            "description": description,
            "participants": []
        }
        self.data["activities"].append(activity)
        self._save_data()
        return activity
    
    def register_user(self, name, location, preferred_categories, available_days):
        """注册用户"""
        user = {
            "id": len(self.data["users"]) + 1,
            "name": name,
            "location": location,
            "preferred_categories": preferred_categories,
            "available_days": available_days,
            "registered_activities": []
        }
        self.data["users"].append(user)
        self._save_data()
        return user
    
    def match_activities(self, user_id):
        """为用户匹配合适的活动"""
        user = next((u for u in self.data["users"] if u["id"] == user_id), None)
        if not user:
            return []
        
        matched = []
        for activity in self.data["activities"]:
            # 检查日期是否在用户可用时间内
            activity_day = datetime.strptime(activity["date"], "%Y-%m-%d").strftime("%A")
            
            # 简化星期匹配逻辑，支持中文和英文星期
            day_matched = False
            for user_day in user["available_days"]:
                if user_day.lower() in activity_day.lower():
                    day_matched = True
                    break
                # 处理中文星期
                chinese_days = {
                    "周一": "Monday", "周二": "Tuesday", "周三": "Wednesday",
                    "周四": "Thursday", "周五": "Friday", "周六": "Saturday", "周日": "Sunday"
                }
                if user_day in chinese_days and chinese_days[user_day].lower() in activity_day.lower():
                    day_matched = True
                    break
            
            # 检查活动类型是否是用户偏好
            category_matched = activity["category"] in user["preferred_categories"]
            
            # 检查地点是否匹配
            location_matched = activity["location"] == user["location"]
            
            # 匹配逻辑调整：放宽条件，只要时间匹配且满足类型或地点其中之一即可
            if day_matched and (category_matched or location_matched):
                matched.append(activity)
        
        return matched
    
    def register_for_activity(self, user_id, activity_id):
        """报名参加活动"""
        user = next((u for u in self.data["users"] if u["id"] == user_id), None)
        activity = next((a for a in self.data["activities"] if a["id"] == activity_id), None)
        
        if not user:
            return "用户不存在"
        if not activity:
            return "活动不存在"
        if activity_id in user["registered_activities"]:
            return "你已报名参加此活动"
        
        user["registered_activities"].append(activity_id)
        activity["participants"].append(user_id)
        self._save_data()
        return f"成功报名参加活动: {activity['name']}"
    
    def list_activities(self):
        """列出所有活动"""
        return self.data["activities"]
    
    def list_user_activities(self, user_id):
        """列出用户报名的所有活动"""
        user = next((u for u in self.data["users"] if u["id"] == user_id), None)
        if not user:
            return []
        
        return [a for a in self.data["activities"] if a["id"] in user["registered_activities"]]

# 初始化应用
matcher = VolunteerActivityMatcher()

# 添加示例数据
if not matcher.data["activities"]:
    today = datetime.now()
    matcher.add_activity(
        "城市公园植树活动", "环保活动", "东城区", 
        (today + timedelta(days=1)).strftime("%Y-%m-%d"), 
        "09:00-12:00", "与社区一起参与城市绿化，为城市增添一抹绿色"
    )
    matcher.add_activity(
        "社区图书馆整理", "教育支持", "西城区", 
        (today + timedelta(days=2)).strftime("%Y-%m-%d"), 
        "14:00-16:30", "协助整理社区图书馆书籍，创造良好阅读环境"
    )
    matcher.add_activity(
        "养老院关爱探访", "关爱老人", "东城区", 
        (today + timedelta(days=6)).strftime("%Y-%m-%d"), 
        "10:00-12:00", "为养老院老人带去欢乐和关爱"
    )
    # 添加更多示例活动以增加匹配可能性
    matcher.add_activity(
        "海滩清洁行动", "环保活动", "南城区", 
        (today + timedelta(days=3)).strftime("%Y-%m-%d"), 
        "08:00-11:00", "保护海洋环境，清理海滩垃圾"
    )
    matcher.add_activity(
        "社区儿童教育", "教育支持", "东城区", 
        (today + timedelta(days=4)).strftime("%Y-%m-%d"), 
        "15:00-17:00", "为社区儿童提供课外辅导和游戏活动"
    )

# Streamlit应用
st.set_page_config(
    page_title="社区志愿活动匹配助手",
    page_icon="🌱",
    layout="wide"
)

# 侧边栏
with st.sidebar:
    st.title("🌱 志愿活动匹配助手")
    st.markdown("---")
    
    page = st.radio(
        "选择功能",
        ["首页", "注册用户", "浏览活动", "查找匹配活动", "报名活动", "我的活动"]
    )
    
    st.markdown("---")
    st.info("💡 提示：通过侧边栏选择不同功能")

# 主页面
if page == "首页":
    st.header("欢迎使用社区志愿活动匹配助手")
    st.write("我们帮助您找到最适合的志愿活动，让您的爱心发挥最大价值")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前活动", len(matcher.list_activities()))
    with col2:
        st.metric("注册用户", len(matcher.data["users"]))
    with col3:
        st.metric("总参与人次", sum(len(a["participants"]) for a in matcher.data["activities"]))
    
    st.image("https://picsum.photos/800/400?random=10", caption="志愿活动照片", use_column_width=True)

elif page == "注册用户":
    st.header("注册新用户")
    
    with st.form("registration_form"):
        name = st.text_input("您的姓名")
        location = st.selectbox("所在区域", ["东城区", "西城区", "南城区", "北城区"])
        
        st.subheader("偏好设置")
        preferred_categories = st.multiselect(
            "偏好的活动类型",
            ["环保活动", "教育支持", "关爱老人", "动物保护", "救灾援助"]
        )
        
        available_days = st.multiselect(
            "空闲时间",
            ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        )
        
        submitted = st.form_submit_button("注册")
        
        if submitted:
            if not name:
                st.error("请输入您的姓名")
            elif not preferred_categories:
                st.error("请至少选择一个偏好的活动类型")
            elif not available_days:
                st.error("请至少选择一个空闲时间")
            else:
                user = matcher.register_user(name, location, preferred_categories, available_days)
                st.success(f"注册成功！您的用户ID是: {user['id']}")
                st.info("请记住您的用户ID，用于后续操作")

elif page == "浏览活动":
    st.header("所有志愿活动")
    
    activities = matcher.list_activities()
    if not activities:
        st.warning("目前没有可用的活动")
    else:
        # 过滤选项
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox("按类型筛选", ["全部"] + list({a["category"] for a in activities}))
        with col2:
            location_filter = st.selectbox("按区域筛选", ["全部"] + list({a["location"] for a in activities}))
        
        # 应用过滤
        filtered_activities = activities
        if category_filter != "全部":
            filtered_activities = [a for a in filtered_activities if a["category"] == category_filter]
        if location_filter != "全部":
            filtered_activities = [a for a in filtered_activities if a["location"] == location_filter]
        
        st.write(f"找到 {len(filtered_activities)} 个活动")
        
        for activity in filtered_activities:
            with st.expander(f"{activity['name']} - {activity['location']}"):
                st.write(f"**类型**: {activity['category']}")
                st.write(f"**日期**: {activity['date']}")
                st.write(f"**时间**: {activity['time_range']}")
                st.write(f"**描述**: {activity['description']}")
                st.write(f"**参与人数**: {len(activity['participants'])}")
                
                # 报名按钮（直接在浏览页面提供报名功能）
                if st.button(f"报名参加 - {activity['name']}"):
                    user_id = st.number_input("请输入您的用户ID", min_value=1, step=1)
                    if st.button("确认报名"):
                        result = matcher.register_for_activity(user_id, activity["id"])
                        if "成功" in result:
                            st.success(result)
                        else:
                            st.error(result)

elif page == "查找匹配活动":
    st.header("查找匹配的志愿活动")
    
    user_id = st.number_input("请输入您的用户ID", min_value=1, step=1)
    
    if st.button("查找匹配活动"):
        user = next((u for u in matcher.data["users"] if u["id"] == user_id), None)
        if not user:
            st.error("用户不存在，请检查您的用户ID")
        else:
            st.markdown(f"### 匹配条件：")
            st.markdown(f"- **所在区域**: {user['location']}")
            st.markdown(f"- **偏好类型**: {', '.join(user['preferred_categories'])}")
            st.markdown(f"- **空闲时间**: {', '.join(user['available_days'])}")
            
            matched = matcher.match_activities(user_id)
            
            if not matched:
                st.warning("没有找到匹配的活动，您可以尝试以下操作：")
                st.markdown("- 扩大您的偏好活动类型范围")
                st.markdown("- 增加您的空闲时间选择")
                st.markdown("- 查看全部活动并手动选择感兴趣的活动")
            else:
                st.success(f"为您找到 {len(matched)} 个匹配的活动")
                for activity in matched:
                    with st.expander(f"{activity['name']} - {activity['location']}"):
                        st.write(f"**类型**: {activity['category']}")
                        st.write(f"**日期**: {activity['date']}")
                        st.write(f"**时间**: {activity['time_range']}")
                        st.write(f"**描述**: {activity['description']}")
                        st.write(f"**参与人数**: {len(activity['participants'])}")
                        
                        if st.button(f"报名参加 - {activity['name']}"):
                            result = matcher.register_for_activity(user_id, activity["id"])
                            if "成功" in result:
                                st.success(result)
                            else:
                                st.error(result)

elif page == "报名活动":
    st.header("报名参加志愿活动")
    
    user_id = st.number_input("您的用户ID", min_value=1, step=1)
    
    activities = matcher.list_activities()
    if not activities:
        st.warning("目前没有可用的活动")
    else:
        # 活动选择
        activity_options = {f"{activity['id']}. {activity['name']} - {activity['location']} ({activity['date']})": activity['id'] for activity in activities}
        selected_activity = st.selectbox("选择要报名的活动", list(activity_options.keys()))
        
        if st.button("报名"):
            activity_id = activity_options[selected_activity]
            result = matcher.register_for_activity(user_id, activity_id)
            
            if "成功" in result:
                st.success(result)
            else:
                st.error(result)

elif page == "我的活动":
    st.header("我的志愿活动")
    
    user_id = st.number_input("您的用户ID", min_value=1, step=1)
    
    if st.button("查看我的活动"):
        my_activities = matcher.list_user_activities(user_id)
        
        if not my_activities:
            st.warning("您还没有报名任何活动")
        else:
            st.success(f"您已报名 {len(my_activities)} 个活动")
            
            # 按日期排序
            my_activities.sort(key=lambda x: x["date"])
            
            for activity in my_activities:
                with st.expander(f"{activity['name']} - {activity['location']}"):
                    st.write(f"**类型**: {activity['category']}")
                    st.write(f"**日期**: {activity['date']}")
                    st.write(f"**时间**: {activity['time_range']}")
                    st.write(f"**描述**: {activity['description']}")
                    st.write(f"**参与人数**: {len(activity['participants'])}")
                    
                    # 取消报名功能
                    if st.button(f"取消报名 - {activity['name']}"):
                        # 从用户已注册活动中移除
                        user = next(u for u in matcher.data["users"] if u["id"] == user_id)
                        if activity["id"] in user["registered_activities"]:
                            user["registered_activities"].remove(activity["id"])
                        
                        # 从活动参与者中移除
                        if user_id in activity["participants"]:
                            activity["participants"].remove(user_id)
                        
                        matcher._save_data()
                        st.success(f"已成功取消报名: {activity['name']}")
                        st.experimental_rerun()    
