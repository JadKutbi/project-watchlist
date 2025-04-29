import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Project Watchlist Generator", layout="wide")
st.title("📂 Project Watchlist Generator + Chatbot")

# رفع ملف المشاريع
uploaded_file = st.file_uploader("📂 قم برفع ملف المشاريع بصيغة Excel:", type=["xlsx"])

if uploaded_file:
    # قراءة ملف المشاريع
    projects_df = pd.read_excel(uploaded_file)

    st.subheader("📋 بيانات جميع المشاريع:")
    st.dataframe(projects_df, use_container_width=True)

    # إنشاء قائمة المراقبة بناءً على المعايير المحددة
    watchlist_conditions = (
        (projects_df['Performance Variance (%)'] <= -15)
    ) | (
        (projects_df['6M Trend Analysis'] == 'Down')
    ) | (
        (projects_df['Tie-in/Interface Delay (days)'] >= 90)
    ) | (
        (projects_df['RC Payment Delay (days)'] >= 90)
    ) | (
        (projects_df['Contractor Salary Delay (days)'] >= 90)
    ) | (
        (100 - projects_df['Manpower Utilization (%)'] >= 40)
    ) | (
        (projects_df['Major Material Delay (days)'] >= 90)
    )

    watchlist_df = projects_df[watchlist_conditions].copy()

    # حساب الأسباب والإجراءات التصحيحية لقائمة المراقبة
    reasons = []
    actions = []

    for idx, row in watchlist_df.iterrows():
        reason_list = []
        action_list = []

        if row['Performance Variance (%)'] <= -15:
            reason_list.append("Significant performance slippage")
            action_list.append("Review project plan and reallocate resources")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Immediately adjust critical path tasks to mitigate slippage")
        if row['6M Trend Analysis'] == 'Down':
            reason_list.append("Consistent negative trend in performance")
            action_list.append("Conduct performance reviews and implement corrective actions")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Prioritize critical path activities in recovery plan")
        if row['Tie-in/Interface Delay (days)'] >= 90:
            reason_list.append("Tie-in/interface issues causing major delays")
            action_list.append("Coordinate early with interfacing teams and expedite approvals")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Escalate tie-in issues to senior management to protect critical path")
        if row['RC Payment Delay (days)'] >= 90:
            reason_list.append("RC payment delays impacting progress")
            action_list.append("Engage with RC finance team to expedite payments")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Prioritize payment clearances for critical path activities")
        if row['Contractor Salary Delay (days)'] >= 90:
            reason_list.append("Contractor salary delays causing workforce instability")
            action_list.append("Ensure timely salary payments through contract management")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Secure manpower for critical path works")
        if (100 - row['Manpower Utilization (%)']) >= 40:
            reason_list.append("Insufficient manpower utilization")
            action_list.append("Mobilize additional workforce and optimize scheduling")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Reallocate manpower to critical path activities")
        if row['Major Material Delay (days)'] >= 90:
            reason_list.append("Major material delivery delays")
            action_list.append("Expedite procurement and logistics processes")
            if row['Affects Critical Path'] == 'Yes':
                action_list.append("Prioritize delivery of materials impacting critical path")

        if not reason_list:
            reason_list.append("Normal Progress")
            action_list.append("Maintain current project management practices")

        reasons.append("; ".join(reason_list))
        actions.append("; ".join(action_list))

    watchlist_df['Reason for Delay'] = reasons
    watchlist_df['Recommended Corrective Action'] = actions

    st.subheader("🚧 المشاريع تحت المراقبة:")
    if not watchlist_df.empty:
        st.dataframe(watchlist_df, use_container_width=True)

        # زر لتحميل ملف قائمة المراقبة
        output_filename = f"watchlist_{datetime.today().strftime('%Y-%m-%d')}.xlsx"
        watchlist_df.to_excel(output_filename, index=False)

        with open(output_filename, "rb") as file:
            st.download_button(
                label="📥 تحميل ملف قائمة المراقبة",
                data=file,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("لا توجد مشاريع تحتاج إلى مراقبة بناءً على البيانات الحالية.")

    st.subheader("🤖 اسأل عن المشاريع:")
    user_query = st.text_input("اكتب سؤالك هنا:")

    if user_query:
        query_lower = user_query.lower()

        if any(word in query_lower for word in ['كل المشاريع', 'all projects']):
            st.write("📋 جميع المشاريع:")
            st.dataframe(projects_df, use_container_width=True)

        elif any(word in query_lower for word in ['ويتش ليست', 'watchlist', 'قائمة المراقبة']):
            st.write("🚧 المشاريع تحت المراقبة:")
            st.dataframe(watchlist_df, use_container_width=True)

        elif 'سبب' in query_lower or 'reason' in query_lower:
            project_id = st.number_input("أدخل رقم المشروع الذي تريد معرفة سبب التأخير له:", min_value=1, max_value=len(watchlist_df), step=1)
            selected_project = watchlist_df.iloc[project_id-1]
            st.success(f"✅ سبب التأخير لمشروع {selected_project['Project Name']} هو: {selected_project['Reason for Delay']}")

        elif 'توصية' in query_lower or 'تصحيح' in query_lower or 'recommend' in query_lower:
            project_id = st.number_input("أدخل رقم المشروع الذي تريد معرفة الإجراء التصحيحي له:", min_value=1, max_value=len(watchlist_df), step=1)
            selected_project = watchlist_df.iloc[project_id-1]
            st.success(f"🛠️ التوصية التصحيحية لمشروع {selected_project['Project Name']} هي: {selected_project['Recommended Corrective Action']}")

        else:
            st.warning("⚠️ لم أفهم سؤالك بدقة. الرجاء استخدام كلمات مثل: كل المشاريع، ويتش ليست، سبب، توصية.")
