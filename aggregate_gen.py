import pymysql
from numpy import median, percentile


class AggregateGenerator:

    def __init__(self):
        # Database credentials
        self.host = "192.168.20.42"
        self.user = "root"
        self.password = "inapp"
        self.db = "perf_forecast"
        self.term_list = ['month', 'year', 'lifetime']

        # Enable / disable aggregate data collection
        self.processordata = "y"
        self.memorydata = "y"
        self.localdiskdata = "y"
        self.internalnetworkdata = "y"

        self.cur = self.db_connection(self.host, self.user, self.password, self.db)

    def db_connection(self, host, user, password, db):
        self.con = pymysql.connect(host, user, password, db)
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        return cur

    def generate_aggregates(self):

        self.cur.execute("SELECT id from xiaoice_virtualmachine")
        results = self.cur.fetchall()

        for result in results:
            if self.processordata == "y":
                table = "xiaoice_processordata"
                field = "performance"
                self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                res = self.cur.fetchone()

                agg_id = self.cur.execute("INSERT INTO xiaoice_processoraggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                self.con.commit()

                for term in self.term_list:
                    output = self.agg_data(term, table, field)
                    self.cur.execute("UPDATE xiaoice_processoraggdata SET %s_min = %s, %s_25 = %s, %s_75 = %s, %s_max = %s, %s_median = %s) WHERE id = %s" % (term, output['resultmin'], term, output['result25'], term, output['result75'], term, output['resultmax'], term, output['resultmedian'], agg_id))

            if self.memorydata == "y":
                table = "xiaoice_memorydata"
                field = "bandwidth"

                for term in self.term_list:
                    output = self.agg_data(term, table, field)

            if self.localdiskdata == "y":
                table = "xiaoice_localdiskdata"

                fields = ['iops_read_seq', 'iops_write_seq', 'iops_read_rand', 'iops_write_rand']
                for field in fields:
                    for term in self.term_list:
                        output = self.agg_data(term, table, field)

            if self.internalnetworkdata == "y":
                table = "xiaoice_internalnetworkdata"

                fields = ['single_threaded_throughput', 'multi_threaded_throughput']
                for field in fields:
                    for term in self.term_list:
                        output = self.agg_data(term, table, field)

    def agg_data(self, term, table, field):

        # Fetches aggregate data for the previous month
        if term is 'prev_month':
            self.cur.execute("SELECT %s FROM %s WHERE YEAR(timestamp) = YEAR(CURDATE() - INTERVAL 1 MONTH) AND MONTH(timestamp) = MONTH(CURDATE() - INTERVAL 1 MONTH)" % (field, table))
        # Fetches aggregate data from one year back to current date
        elif term is 'prev_year':
            self.cur.execute("SELECT %s FROM %s WHERE timestamp BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()" % (field, table))
        # Fetches aggregate data from the beginning to current date
        elif term is 'lifetime':
            self.cur.execute("SELECT %s FROM %s" % (field, table))

        results = self.cur.fetchall()
        results = [element for tupl in results for element in tupl]
        results = filter(None, results)

        output = []
        if results:
            output['resultmin'] = min(results)
            output['result25'] = percentile(results, 25)
            output['resultmedian'] = median(results)
            output['result75'] = percentile(results, 75)
            output['resultmax'] = max(results)
            print "\n===== Table: %s ===== Field: %s ===== Term: %s =====\n" % (table, field, term)
            print "min,25th,median,75th,max"
            print "%s,%s,%s,%s,%s" % (output['resultmin'], output['result25'], output['resultmedian'], output['result75'], output['resultmax'])
        return output

agg = AggregateGenerator()
agg.generate_aggregates()
