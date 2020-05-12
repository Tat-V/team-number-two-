from datetime import datetime, date, timedelta
import Shushushu as sh
import pymongo


class Files:
    HistoryFile = "source_pack./History.txt"
    AdminHistoryFile = "source_pack/Admin_History.txt"
    FilmFile = 'source_pack/Film Library.txt'

    @staticmethod
    def new_log(self, update, funcname):
        sh.LOG_ACTIONS.append({
            'user': update.effective_user.first_name,
            'user id': update.message.chat.id,
            'function': funcname,
            'message': update.message.text,
            'time': datetime.now().strftime("%Y-%m-%d %H.%M")})
        sh.collection.insert_one({
            'user': update.effective_user.first_name,
            'user id': update.message.chat.id,
            'function': funcname,
            'message': update.message.text,
            'time': datetime.now().strftime("%Y-%m-%d %H.%M")})
        if str(sh.LOG_ACTIONS[-1]['function']).find('admin') == -1:
            with open(Files.HistoryFile, "a", encoding="UTF-8") as file_h:
                for key, value in sh.LOG_ACTIONS[-1].items():
                    file_h.write(key + ':' + (str(value)) + "\t")
                file_h.write("\n")
        elif str(sh.LOG_ACTIONS[-1]['function']).find('admin') != -1:
            with open(Files.AdminHistoryFile, "a", encoding="UTF-8") as handler:
                for key, value in sh.LOG_ACTIONS[-1].items():
                    handler.write(key + ':' + (str(value)) + "\t")
                handler.write("\n")

    @staticmethod
    def history(self):
        """Send user last 5 records from history."""
        # hist = ""
        # with open(files.HistoryFile, "r", encoding="UTF-8") as file_h:
        #     hist_all = file_h.readlines()
        #     if len(hist_all) > 4:
        #         for i in range(-1, -6, -1):
        #             hist += hist_all[i]
        #     else:
        #         hist = "\t".join(hist_all)
        # return hist
        hist = []
        for idx, user in enumerate(sh.collection.find().sort("_id", pymongo.DESCENDING).limit(5)):
            if idx == 5:
                break
            hist.append("\t".join([key + "\t" + str(user[key]) for key in user if key != "_id"]))
        hist_st = "\n".join(hist)
        return hist_st

    @staticmethod
    def delete_logs(self):
        k = 0
        with open(Files.HistoryFile, "r", encoding="UTF-8") as file_h:
            hist_all = file_h.readlines()
        for hist_line in hist_all:
            hist_line = hist_line.split('\t')
            hist_time = hist_line[-2].replace('time:', '')
            hist_time = datetime.strptime(hist_time, "%Y-%m-%d %H.%M")
            now = datetime.now()
            period = now - hist_time
            print(period)
            if period.days < 7:
                break
            k += 1
            print(k)
        with open(Files.HistoryFile, 'w') as file_h:
            file_h.writelines(hist_all[k:])
