import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.ticker as ticker
from datetime import date
from io import BytesIO

def main_zh():
    
    ### Init ###

    font_prop = FontProperties(fname='./NotoSansCJK-Regular.ttc')

    # 初始化數據，如果 st.session_state 中沒有存儲數據

    if 'data' not in st.session_state:

        sample_data = [
        {'項目名稱': '基礎構造', '花費金額': 50000, '起始日期': '2024-07-01', '持續天數': 5, '結束日期': ''},
        {'項目名稱': '結構加固', '花費金額': 120000, '起始日期': '2024-07-15', '持續天數': 12, '結束日期': ''},
        {'項目名稱': '地基工程', '花費金額': 80000, '起始日期': '2024-08-01', '持續天數': 8, '結束日期': ''},
        {'項目名稱': '屋頂修復', '花費金額': 100000, '起始日期': '2024-07-01', '持續天數': 10, '結束日期': ''},
        {'項目名稱': '室內裝修', '花費金額': 60000, '起始日期': '2024-07-05', '持續天數': 6, '結束日期': ''},
        {'項目名稱': '電力系統升級', '花費金額': 70000, '起始日期': '2024-07-20', '持續天數': 7, '結束日期': ''},
        {'項目名稱': '水利設施建設', '花費金額': 90000, '起始日期': '2024-07-25', '持續天數': 9, '結束日期': ''},
        {'項目名稱': '道路擴建', '花費金額': 110000, '起始日期': '2024-08-05', '持續天數': 11, '結束日期': ''},
        {'項目名稱': '綠化工程', '花費金額': 80000, '起始日期': '2024-08-10', '持續天數': 8, '結束日期': ''},
        {'項目名稱': '消防安全系統', '花費金額': 90000, '起始日期': '2024-08-15', '持續天數': 9, '結束日期': ''},
        ]

        st.session_state['data']=sample_data

    col1, col2 = st.columns([1, 2])

    with col1:

        st.markdown("### :spiral_calendar_pad: 工程進度甘特圖 V0.1.0")
        st.info("作者: HankLin  ,  [作者聯絡資訊](https://hanksvba.com)")
        with st.expander(":tv: 影片操作教學"):
            st.video("demo.mp4")
        st.markdown("---")

        # 總表（編輯方式），回饋到 st.session_state
        st.markdown("##### 	:point_down: 施工項目填寫")

        df=pd.DataFrame(st.session_state['data'])

        df['起始日期'] = pd.to_datetime(df['起始日期'])

        edited_df = st.data_editor(df, use_container_width=True,num_rows='dynamic',
                                column_config={
                                    "起始日期": st.column_config.DateColumn(
                                        "起始日期",
                                        min_value=date(2024, 1, 1),
                                        max_value=date(2030, 1, 1),
                                        format="YYYY-MM-DD",
                                        step=1,
                                    )
                                },
                                hide_index=True, column_order=("項目名稱", "花費金額", "起始日期", "持續天數"))

        edited_df['結束日期'] = edited_df['起始日期'] + pd.to_timedelta(edited_df['持續天數'], unit='D')

        is_show_text=st.toggle("圖塊文字")


    ### 計算流程以下都沒問題 ###

    final_df=edited_df

    if len(final_df)==0:
        exit()
    else:
        # 計算每日耗費成本
        total_cost = final_df['花費金額'].sum()
        start_date = final_df['起始日期'].min()
        end_date = final_df['結束日期'].max()
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')  # 每日頻率
        daily_cost = np.zeros(len(date_range))

        for i, row in final_df.iterrows():
            cost_per_day = row['花費金額'] / row['持續天數']
            daily_cost[(date_range > row['起始日期']) & (date_range <= row['結束日期'])] += cost_per_day

        # 計算累積花費金額和每日進度百分比
        cumulative_cost = np.cumsum(daily_cost)

        daily_progress = (daily_cost / total_cost) * 100
        cumulative_progress = (cumulative_cost / total_cost) * 100

        csv_data = pd.DataFrame({
            '日期': date_range,
            '當日費用': daily_cost,
            '累積費用': cumulative_cost,
            '當日進度': daily_progress,
            '累積進度': cumulative_progress
        })

    with col2:

        fig, ax1 = plt.subplots(figsize=(14, 10))

        # 畫甘特圖，調整顏色和透明度，加入格線
        colors = plt.cm.Set3.colors  # 使用單一色系

        cnt=0
        for i, row in final_df.iterrows():
            if not pd.isna(row["持續天數"]):
                color = colors[i % len(colors)]
                ax1.barh(row['項目名稱'], row['持續天數'], left=row['起始日期'], height=0.3, color=color)
                if is_show_text==True:
                    ax1.text(row['起始日期'], cnt, f"{row['項目名稱']}: {int(row['持續天數'])}天", color='black', verticalalignment='center', fontsize=10, fontproperties=font_prop)
                cnt=cnt+1

        # 設置標籤和標題
        ax1.set_xlabel('日期', fontproperties=font_prop)
        ax1.set_title('施工進度甘特圖', fontproperties=font_prop)

        for label in ax1.get_yticklabels():
            label.set_fontproperties(font_prop)

        # 在同一張圖上繪製每日累積進度圖並標示節點百分比
        ax2 = ax1.twinx()
        ax2.plot(date_range, cumulative_progress, marker='o', linestyle='-', color='orange')
        for i, txt in enumerate(cumulative_progress):
            if i % 5== 0 or txt==100:  # 每10%標示一次
                ax2.annotate(f'{int(txt)}%', (date_range[i], cumulative_progress[i]), textcoords="offset points", xytext=(0,10), ha='center', fontproperties=font_prop)

        ax2.set_ylabel('累積進度百分比 (%)', fontproperties=font_prop)
        ax2.yaxis.set_major_locator(ticker.MultipleLocator(base=10))
        # 調整 x 軸日期顯示為每半個月
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))  # 每10顯示一次日期
        ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  # 每天都顯示日期
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # 添加網格線
        ax2.grid(True, which='both', linestyle=':', linewidth=0.5)

        # 添加圖例，將位置調整到右下角
        # ax1.legend(['工程項目'], loc='upper left', prop=font_prop)
        ax2.legend(['累積進度'], loc='lower right', prop=font_prop)

        # 調整圖形排版
        fig.tight_layout()

        ax1.set_xlim(start_date - pd.Timedelta(days=3), end_date + pd.Timedelta(days=3))

        # 顯示圖形
        st.pyplot(fig)

    # # 下載 CSV 按鈕
    # csv_data = pd.DataFrame({
    #     'date': date_range,
    #     'progress(%)': daily_progress/100,
    #     'sum_progress(%)': cumulative_progress/100
    # })
    # csv_data['date'] = csv_data['date'].dt.strftime('%Y-%m-%d')  # 將日期轉換為字串格式
    # csv_string = csv_data.to_csv(index=False, encoding='utf-8-sig')

    # 產生 Excel 資料
    excel_data = pd.DataFrame({
        'date': date_range,
        'progress(%)': daily_progress/100,
        'sum_progress(%)': cumulative_progress/100
    })
    excel_data['date'] = excel_data['date'].dt.strftime('%Y-%m-%d')  # 將日期轉換為字串格式

    # 將 DataFrame 轉換為 Excel 格式
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Progress Data')
        return output.getvalue()


    # 提供下載按鈕

    with col1:

        # st.download_button(
        #     label="下載 CSV 檔案",
        #     data=csv_string,
        #     file_name='progress_data.csv',
        #     mime='text/csv'
        # )

        # 下載 Excel 按鈕
        excel_data_bytes = to_excel(excel_data)
        st.download_button(
            label="下載 Excel 檔案",
            data=excel_data_bytes,
            file_name='progress_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


if __name__ == "__main__":
    
    st.set_page_config(layout='wide')

    main_zh()