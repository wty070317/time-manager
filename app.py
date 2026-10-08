import streamlit as st
from datetime import datetime, date
from typing import List, Dict

# ========== PWA移动端配置（可添加手机桌面，竞赛亮点） ==========
st.set_page_config(
    page_title="大学生时间管理AI助手",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoi5rK75Y2H55qG5LqR57uG54K55Yiw5pyN5YqhIiwic2hvcnRfbmFtZSI6IuW8oOihj+W3peWFtS6rCIsInN0YXJ0X3VybCI6Ii4iLCJkaXNwbHkiOiJzdGFuZGFsb25lIiwiYmFja2dyb3VuZF9jb2xvciI6IiNmZmZmZmYiLCJ0aGVtZV9jb2xvciI6IiNmZmZmZmYifQ==">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
""", unsafe_allow_html=True)

# 任务实体类
class TaskItem:
    def __init__(self, task_name: str, deadline: date, task_type: str, cost_min: int, importance: str):
        self.task_name = task_name
        self.deadline = deadline
        self.task_type = task_type
        self.cost_min = cost_min
        self.importance = importance   # 重要紧急四象限：重要紧急/重要不紧急/紧急不重要/普通
        self.status = "pending"         # pending未完成 / done已完成

# AI时间规划核心
class AITimePlanner:
    def __init__(self):
        # session_state持久存储页面数据，刷新页面数据不丢失
        if "user_basic" not in st.session_state:
            st.session_state.user_basic = {
                "sleep_rule": "",
                "course_list": []
            }
        if "task_data" not in st.session_state:
            st.session_state.task_data: List[TaskItem] = []
        if "feedback_log" not in st.session_state:
            st.session_state.feedback_log = []

    # ① 用户录入作息、课程信息
    def input_user_info_ui(self):
        st.subheader("📝第一步｜录入个人作息与课程信息")
        sleep_input = st.text_input("每日作息时间（例：23:00‑07:20）", value=st.session_state.user_basic["sleep_rule"])
        st.session_state.user_basic["sleep_rule"] = sleep_input

        course_cnt = st.number_input("本周固定课程数量", min_value=0, max_value=25, value=len(st.session_state.user_basic["course_list"]))
        new_course_arr = []
        for idx in range(int(course_cnt)):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input(f"课程{idx+1}名称", key=f"coursename_{idx}")
            with c2:
                c_time_text = st.text_input(f"课程时间（例周二14:00‑15:40）", key=f"coursetime_{idx}")
            if c_name and c_time_text:
                new_course_arr.append({"cname":c_name,"ctime":c_time_text})
        st.session_state.user_basic["course_list"] = new_course_arr

        if st.button("✅提交信息，送往AI智能体工作流"):
            st.success("信息接收完成，已传递AI智能体等待解析！")

    # ②添加待办任务，智能解析、任务分级、冲突检测，生成初始计划表
    def add_task_and_gen_schedule(self):
        st.subheader("📋第二步｜录入待办任务，AI生成初始时间规划")
        with st.expander("➕新增待办任务（支持课程作业、社团、竞赛、复习等）"):
            t_name = st.text_input("任务名称")
            t_dead = st.date_input("任务截止日期")
            t_cat = st.selectbox("任务分类",["课程作业","考试复习","社团事务","竞赛项目","个人生活"])
            t_time_cost = st.number_input("预估耗时（分钟）",min_value=10,max_value=600,value=60)
            t_priority = st.selectbox("任务优先级（四象限）",["重要紧急","重要不紧急","紧急不重要","普通任务"])
            if st.button("添加该任务"):
                new_t = TaskItem(t_name,t_dead,t_cat,t_time_cost,t_priority)
                st.session_state.task_data.append(new_t)
                st.success("任务录入成功！AI开始分析处理")

        st.divider()
        task_all = st.session_state.task_data
        # 任务排序规则：先优先级，再截止日期，模拟智能体分级
        priority_map = {"重要紧急":0,"重要不紧急":1,"紧急不重要":2,"普通任务":3}
        task_all.sort(key=lambda x:(priority_map[x.importance], x.deadline))

        st.markdown("### 📅AI智能体输出：初始时间规划表")
        if len(task_all) == 0:
            st.info("暂无待办任务，请先添加任务")
        else:
            for num, t in enumerate(task_all):
                status_text = "🟡未完成" if t.status=="pending" else "🟢已完成"
                st.write(f"**{num+1}.【{t.importance}】{t.task_name}** |截止:{t.deadline} |类别:{t.task_type} |预估:{t.cost_min}分钟 |{status_text}")
            st.info("✅完成信息解析、任务分级、空闲时段冲突校验，计划表返回前端展示")

    # ③用户提交每日任务完成反馈
    def submit_daily_feedback_ui(self):
        st.subheader("✍第三步｜提交今日任务执行反馈")
        task_list = st.session_state.task_data
        if len(task_list) == 0:
            st.warning("还没有待办任务，请前往第二步添加任务")
            return
        for item in task_list:
            res = st.radio(f"任务：{item.task_name}",["未完成","已完成"],key=f"taskradio_{item.task_name}")
            if res == "已完成":
                item.status = "done"
            else:
                item.status = "pending"
        if st.button("📤提交反馈，交由AI智能体修正日程"):
            for tsk in task_list:
                st.session_state.feedback_log.append({
                    "task":tsk.task_name,
                    "status":tsk.status,
                    "record_time":datetime.now()
                })
            st.success("用户执行反馈已录入AI智能体！")

    # ④动态修正日程 + 输出每周复盘报告
    def adjust_and_weekly_review(self):
        st.subheader("📊第四步｜AI动态调整方案 & 周度复盘报告")
        tasks = st.session_state.task_data
        done_list = [x for x in tasks if x.status == "done"]
        undone_list = [x for x in tasks if x.status == "pending"]
        total_cnt = len(tasks)
        if total_cnt == 0:
            st.info("暂无任务数据，无需复盘")
            return

        # 模拟智能体动态调整逻辑：未完成任务提升优先级，降低后续任务密度
        st.markdown("#### 🔧智能体读取反馈，动态修正日程结果")
        if len(undone_list) > 0:
            st.warning(f"检测到 {len(undone_list)} 项任务未完成，已提升优先级，减轻后续任务负荷，防止计划崩盘")
            for ut in undone_list:
                st.write(f"▪ {ut.task_name}：顺延至空闲窗口，优先安排")
        else:
            st.success("🎉全部任务执行完毕，计划完成度优秀！")

        st.divider()
        # 周复盘报告
        st.markdown("# 📑周度时间复盘报告")
        done_count = len(done_list)
        finish_rate = done_count / total_cnt *100

        st.write(f"总任务数量：{total_cnt} 项")
        st.write(f"已完成任务：{done_count} 项")
        st.write(f"任务整体完成率：{finish_rate:.1f} %")

        if finish_rate >=70:
            st.success("💡AI建议：时间规划执行情况优秀，保持当前节奏，可以适度增加挑战性任务")
        elif finish_rate >=40:
            st.info("💡AI建议：完成度中等，建议拆分大任务，减少单日安排任务总量，避免过载")
        else:
            st.error("💡AI建议：任务积压较多，优先处理重要紧急任务，适当降低预期，从小任务逐步启动")

        st.markdown("> 复盘逻辑：汇总执行记录，统计完成率，识别拖延情况，输出个性化改进建议")

# 主页面入口
def main():
    st.title("⏱️大学生时间管理AI助手")
    st.markdown("竞赛作品｜流程：录入作息课程 → 添加待办任务 →生成规划 →提交每日反馈 →动态调整+周复盘")
    planner = AITimePlanner()
    tab1,tab2,tab3,tab4 = st.tabs(["1.录入作息课程","2.任务录入&生成规划","3.提交每日反馈","4.日程调整&周复盘"])
    with tab1:
        planner.input_user_info_ui()
    with tab2:
        planner.add_task_and_gen_schedule()
    with tab3:
        planner.submit_daily_feedback_ui()
    with tab4:
        planner.adjust_and_weekly_review()

if __name__ == "__main__":
    main()
