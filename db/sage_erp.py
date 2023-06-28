from .db import DB, DBError
import pyodbc
from datetime import datetime


class SageERP:
    """
    This class is used to connect to the Sage ERP database,
    and provide data views.
    """
    db = None
    appusers = 0
    biusers = 0

    def __init__(self):
        self.db = DB()
        self.connection = self.db.connection
        super().__init__()

    def get_sage_erp_users(self):
        """
        Get the list of Sage ERP users
        """
        try:
            cursor = self.connection.cursor()
            sqlcmd = """
                DECLARE @_DBName VARCHAR(255) = 'mas500_app';

                WITH CTE AS (
                    SELECT
                        login_name as Username,
                        host_name as workstation,
                        login_time,
                        last_request_start_time,

                        CASE
                            WHEN database_id = db_id(@_DBName) AND program_name LIKE 'Sage 500 ERP/App%' THEN 'X'
                            ELSE ' '
                        END as AppUser,
                        CASE
                            WHEN database_id = db_id(@_DBName) AND program_name LIKE 'Sage 500 ERP/Business Insight%' THEN 'X'
                            ELSE ' '
                        END as BIUser
                    FROM
                        sys.dm_exec_sessions with (nolock)
                )
                SELECT
                    Username,
                    workstation,
                    login_time,
                    last_request_start_time as Last_Activty,
                    AppUser,
                    BIUser
                FROM
                    CTE
                WHERE
                    AppUser <> ' ' OR BIUser <> ' ';
            """
            cursor.execute(sqlcmd)
        except pyodbc.Error as err:
            raise DBError(f'Error executing query:{err}')

        try:
            rows = cursor.fetchall()
        except pyodbc.Error as err:
            raise DBError(f'Error fetching rows:{err}')

        users = list()

        for row in rows:
            try:
                users.append(self.db.extract_row(row))
            except Exception as err:
                print(f'Error extracting row: {err}')
                users.append({'error': f'Error extracting row: {err}'})

        self.appusers = 0
        self.biusers = 0
        for u in users:
            if u['appuser'] == 'X':
                self.appusers += 1
            if u['biuser'] == 'X':
                self.biusers += 1
            u['username'] = self.remove_domain(u['username'])

            u['login_time'] = self.reformat_datetime(u['login_time'].__str__())
            u['last_activty'] = self.reformat_datetime(u['last_activty'].__str__())
            u['sort_key'] = datetime.strptime(u['last_activty'], '%m/%d/%Y %I:%M %p')

        users = self.sort_users(users)

        return users

    @staticmethod
    def remove_domain(user):
        """
        Remove the domain from the user name
        """
        if user.find('\\') > 0:
            return user.split('\\')[1]
        return user

    @staticmethod
    def reformat_datetime(dt: str):
        """
        Reformat the datetime string from YYYY-MM-DD HH:MM:SS.Z to MM/DD/YYYY HH:MM AM/PM
        """
        if dt is None:
            return ''
        datetime_tmp = dt.replace('T', ' ').replace('Z', '')

        # check to see if .%f is in the string, and add it if not
        if not('.' in datetime_tmp):
            datetime_tmp = f'{datetime_tmp}.000000'

        dtmp = None
        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
            try:
                dtmp = datetime.strptime(datetime_tmp, fmt)
                break
            except Exception as err:
                print(f'Error in reformat_datetime: {err}')
                pass

        if dtmp is None:
            result = ''
        else:
            result = dtmp.strftime('%m/%d/%Y %I:%M %p')

        return result

    @staticmethod
    def sort_users(users):
        """
        Sort the users by sort_key
        """
        return sorted(users, key=lambda k: k['sort_key'])