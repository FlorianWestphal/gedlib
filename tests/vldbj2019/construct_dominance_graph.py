import csv
from pickle import NONE
import argparse
from decimal import Decimal
import os.path

def computes_no_lb(method_name):
    if method_name == "BP":
        return True
    elif method_name == "SUBGRAPH":
        return True
    elif method_name == "WALKS":
        return True
    elif method_name == "RINGOPT":
        return True
    elif method_name == "RINGMS":
        return True
    elif method_name == "RINGMLDNN":
        return True
    elif method_name == "RINGMLSVM":
        return True
    elif method_name == "PREDICTDNN":
        return True
    elif method_name == "PREDICTSVM":
        return True
    elif method_name == "REFINE":
        return True
    elif method_name == "KREFINE":
        return True
    elif method_name == "BPBEAM":
        return True
    elif method_name == "IBPBEAM":
        return True
    elif method_name == "IPFP":
        return True
    elif method_name == "SA":
        return True
    else:
        return False

def computes_no_ub(method_name):
    if method_name == "HED":
        return True
    elif method_name == "BRANCHCOMPACT":
        return True
    elif method_name == "PARTITION":
        return True
    elif method_name == "HYBRID":
        return True
    else:
        return False

def is_ls_based(method):
    if method.name == "REFINE":
        return True
    elif method.name == "KREFINE":
        return True
    elif method.name == "BPBEAM":
        return True
    elif method.name == "IBPBEAM":
        return True
    elif method.name == "IPFP":
        return True
    elif method.name == "SA":
        return True
    else:
        return False

def is_lsape_based(method):
    if method.name == "BP":
        return True
    elif method.name == "BRANCH":
        return True
    elif method.name == "BRANCHFAST":
        return True
    elif method.name == "BRANCHUNI":
        return True
    elif method.name == "STAR":
        return True
    elif method.name == "NODE":
        return True
    elif method.name == "SUBGRAPH":
        return True
    elif method.name == "WALKS":
        return True
    elif method.name == "RINGOPT":
        return True
    elif method.name == "RINGMS":
        return True
    elif method.name == "RINGMLDNN":
        return True
    elif method.name == "RINGMLSVM":
        return True
    elif method.name == "PREDICTDNN":
        return True
    elif method.name == "PREDICTSVM":
        return True
    else:
        return False
    
def uses_randpost(method):
    if is_ls_based(method):
        return (int(method.config[2:-2].split(",")[2]) > 0)
    else:
        return False
    
def uses_multi_start(method):
    if is_ls_based(method):
        return (int(method.config[2:-2].split(",")[0]) > 1)
    else:
        return False

def uses_multi_sol(method):
    if is_lsape_based(method):
        return (int(method.config[2:-2].split(",")[0]) > 1)
    else:
        return False

def uses_centralities(method):
    if is_lsape_based(method):
        return (float(method.config[2:-2].split(",")[1]) > 0)
    else:
        return False

class Method:
    
    def __init__(self, name, lb, ub, t, coeff_lb, coeff_ub):
        self.consider_lb = True
        self.name = name[0]
        self.config = name[1]
        self.lb = float("{:.2E}".format(Decimal(lb)))
        self.ub = float("{:.2E}".format(Decimal(ub)))
        self.t = float("{:.2E}".format(Decimal(str(float(t)*1000.0))))
        self.coeff_lb = float("{:.2}".format(Decimal(coeff_lb)))
        self.coeff_ub = float("{:.2}".format(Decimal(coeff_ub)))
        self.is_fastest_lb = not computes_no_lb(self.name)
        self.is_fastest_ub = not computes_no_ub(self.name)
        self.has_tightest_lb = not computes_no_lb(self.name)
        self.has_tightest_ub = not computes_no_ub(self.name)
        self.has_best_coeff_lb = not computes_no_lb(self.name)
        self.has_best_coeff_ub = not computes_no_ub(self.name)
        self.is_maximum_lb = not computes_no_lb(self.name)
        self.is_maximum_ub = not computes_no_ub(self.name)
        self.discard_for_lb = computes_no_lb(self.name)
        self.discard_for_ub = computes_no_ub(self.name)
        self.score_lb = 0
        self.score_ub = 0
        self.adj_list_lb = []
        self.adj_list_ub = []
            
    def stats(self):
        method_stats = "$t=\\SI{" + "{:.2E}".format(Decimal(str(self.t))) + "}{\milli\second}$\\\\"
        if self.consider_lb:
            method_stats = method_stats + "$d_{\LB}=\\num{" + "{:.2E}".format(Decimal(str(self.lb))) + "}$\\\\"
        else:
            method_stats = method_stats + "$d_{\UB}=\\num{" + "{:.2E}".format(Decimal(str(self.ub))) + "}$\\\\"
        if self.consider_lb:
            method_stats = method_stats + "$c_{\LB}=\\num{" + "{:.2}".format(Decimal(str(self.coeff_lb))) + "}$\\\\"
            method_stats = method_stats + "$s_{\LB}=\\num{" + "{:.2}".format(Decimal(str(self.score_lb))) + "}$"
        else:
            method_stats = method_stats + "$c_{\UB}=\\num{" + "{:.2}".format(Decimal(str(self.coeff_ub))) + "}$\\\\"
            method_stats = method_stats + "$s_{\UB}=\\num{" + "{:.2}".format(Decimal(str(self.score_ub))) + "}$"
        return method_stats
    
    def tikz_descriptor(self):
        descriptor = "\\" + self.name + "\\\\"
        if self.config != "":
            descriptor = descriptor + self.config
        if self.consider_lb and self.is_maximum_lb:
            descriptor = descriptor + "\\\\" + self.stats()
        if (not self.consider_lb) and self.is_maximum_ub:
            descriptor = descriptor + "\\\\" + self.stats()
        return descriptor
    
    def label(self):
        labels = []
        if self.consider_lb and self.has_tightest_lb:
            labels.append("\\textcolor{Blue}{$d^\star_{\LB}$}")
        if (not self.consider_lb) and self.has_tightest_ub:
            labels.append("\\textcolor{Blue}{$d^\star_{\UB}$}")
        if self.consider_lb and self.is_fastest_lb:
            labels.append("\\textcolor{Red}{$t^\star_{\LB}$}")
        if (not self.consider_lb) and self.is_fastest_ub:
            labels.append("\\textcolor{Red}{$t^\star_{\UB}$}")
        if self.consider_lb and self.has_best_coeff_lb:
            labels.append("\\textcolor{Green}{$c^\star_{\LB}$}")
        if (not self.consider_lb) and self.has_best_coeff_ub:
            labels.append("\\textcolor{Green}{$c^\star_{\UB}$}")
        if len(labels) == 0:
            return ""
        label = labels[0]
        for index in range(1, len(labels)):
            label = label + " " + labels[index]
        return label
    
    def compare_tightness(self, other):
        if self.consider_lb:
            if self.lb > other.lb:
                return 1
            elif self.lb == other.lb:
                return 0
            else:
                return -1
        else:
            if self.ub < other.ub:
                return 1
            elif self.ub == other.ub:
                return 0
            else:
                return -1
    
    def compare_time(self, other):
        if self.t < other.t:
            return 1
        elif self.t == other.t:
            return 0
        else:
            return -1
        
    def compare_coeff(self, other):
        if self.consider_lb:
            if self.coeff_lb > other.coeff_lb:
                return 1
            elif self.coeff_lb == other.coeff_lb:
                return 0
            else:
                return -1
        else:
            if self.coeff_ub > other.coeff_ub:
                return 1
            elif self.coeff_ub == other.coeff_ub:
                return 0
            else:
                return -1
    
    def get_edge_label(self, other):
        is_better_or_equal = True
        if self.compare_tightness(other) < 0:
            is_better_or_equal = False
            if self.consider_lb:
                self.has_tightest_lb = False
            else:
                self.has_tightest_ub = False
        if self.compare_time(other) < 0:
            is_better_or_equal = False
            if self.consider_lb:
                self.is_fastest_lb = False
            else:
                self.is_fastest_ub = False
        if self.compare_coeff(other) < 0:
            is_better_or_equal = False
            if self.consider_lb:
                self.has_best_coeff_lb = False
            else:
                self.has_best_coeff_ub = False
        label = ""
        if self.compare_tightness(other) > 0:
            if self.consider_lb:
                other.has_tightest_lb = False
            else:
                other.has_tightest_ub = False
            label = label + "d"
        if self.compare_time(other) > 0:
            if self.consider_lb:
                other.is_fastest_lb = False
            else:
                other.is_fastest_ub = False
            label = label + "t"
        if self.compare_coeff(other) > 0:
            if self.consider_lb:
                other.has_best_coeff_lb = False
            else:
                other.has_best_coeff_ub = False
            label = label + "c"
        if is_better_or_equal and (label != ""):
            if self.consider_lb:
                other.is_maximum_lb = False
                if self.name == other.name:
                    other.discard_for_lb = True
            else:
                other.is_maximum_ub = False
                if self.name == other.name:
                    other.discard_for_ub = True
        if is_better_or_equal:
            return label
        else:
            return ""
    
    def as_table_row(self):
        table_row = "\\" + self.name
        if self.is_maximum_lb:
            table_row = table_row + " $\LB^\star$"
        if self.is_maximum_ub:
            table_row = table_row + " $\UB^\star$"
        if self.config != "":
            table_row = table_row + " & " + self.config
        else:
            table_row = table_row + " & {--}"
        if not computes_no_lb(self.name):
            table_row = table_row + " & " + "{:.2E}".format(Decimal(str(self.lb)))
        else:
            table_row = table_row + " & {--}"
        if not computes_no_ub(self.name):
            table_row = table_row + " & " + "{:.2E}".format(Decimal(str(self.ub)))
        else:
            table_row = table_row + " & {--}"
        table_row = table_row + " & " + "{:.2E}".format(Decimal(str(self.t)))
        if not computes_no_lb(self.name):
            table_row = table_row + " & " + "{:.2}".format(Decimal(str(self.coeff_lb)))
        else:
            table_row = table_row + " & {--}"
        if not computes_no_ub(self.name):
            table_row = table_row + " & " + "{:.2}".format(Decimal(str(self.coeff_ub)))
        else:
            table_row = table_row + " & {--}"
        if not computes_no_lb(self.name):
            table_row = table_row + " & " + "{:.2}".format(Decimal(str(self.score_lb)))
        else:
            table_row = table_row + " & {--}"
        if not computes_no_ub(self.name):
            table_row = table_row + " & " + "{:.2}".format(Decimal(str(self.score_ub)))
        else:
            table_row = table_row + " & {--}"
        table_row = table_row + " \\\\\n"
        return table_row
    
    def is_maximum(self):
        if self.consider_lb:
            return self.is_maximum_lb
        else:
            return self.is_maximum_ub
    
    def dist(self):
        if self.consider_lb:
            return self.lb
        else:
            return self.ub
    
    def coeff(self):
        if self.consider_lb:
            return self.coeff_lb
        else:
            return self.coeff_ub
    
    def has_tightest_dist(self):
        if self.consider_lb:
            return self.has_tightest_lb
        else:
            return self.has_best_coeff_ub
        
    def is_fastest(self):
        if self.consider_lb:
            return self.is_fastest_lb
        else:
            return self.is_fastest_ub
        
    def has_best_coeff(self):
        if self.consider_lb:
            return self.has_best_coeff_lb
        else:
            return self.has_best_coeff_ub
    
    def discard(self):
        if self.consider_lb:
            return self.discard_for_lb
        else:
            return self.discard_for_ub
    
    def get_adj_list(self):
        if self.consider_lb:
            return self.adj_list_lb
        else:
            return self.adj_list_ub
    
    def set_adj_list(self, new_adj_list):
        if self.consider_lb:
            self.adj_list_lb = new_adj_list
        else:
            self.adj_list_ub = new_adj_list
    
    def set_score(self, best_dist, best_t, best_coeff):
        if self.consider_lb:
            self.score_lb = ((self.lb / best_dist) + (best_t / self.t) + (self.coeff_lb / best_coeff)) / 3.0
        else:
            self.score_ub = ((best_dist / self.ub) + (best_t / self.t) + (self.coeff_ub / best_coeff)) / 3.0
            
        

def parse_method_name(method_name):
    method_name_list = method_name.split(",", 1)
    if (len(method_name_list) == 1):
        method_name_list.append("")
    return method_name_list

def dfs(methods, is_discarded_edge, parent_id, child_id, seen):
    if seen[child_id]:
        return
    for edge in methods[child_id].get_adj_list():
        is_discarded_edge[parent_id][edge[0]] = True;
        dfs(methods, is_discarded_edge, parent_id, edge[0], seen)
    seen[child_id] = True
    
def read_results_from_csv_files(args):
    methods = []
    result_file_names = []
    prefix = os.path.join("results", args.dataset) + "__"
    if args.lsape:
        result_file_names.append(prefix + "lsape_based_methods.csv")
    if args.ls:
        result_file_names.append(prefix + "ls_based_methods.csv")
    if args.lp:
        result_file_names.append(prefix + "lp_based_methods.csv")
    if args.misc:
        result_file_names.append(prefix + "misc_methods.csv")
    for result_file_name in result_file_names:
        with open(result_file_name, "r") as result_file:  
            csv_reader = csv.reader(result_file,delimiter=";")
            next(csv_reader, NONE)
            for row in csv_reader:
                methods.append(Method(parse_method_name(row[0]), row[1], row[2], row[3], row[4], row[5]))
    return methods

def build_dependency_graph(methods, consider_lb):
    # set consider_lb for all methods
    for method in methods:
        method.consider_lb = consider_lb
    # construct dominance graph
    num_methods = len(methods)
    adj_list = [[] for method_id in range(0,num_methods)]
    for id_1 in range(0, num_methods):
        method_1 = methods[id_1]
        new_adj_list = []
        if not method_1.discard():
            for id_2 in range(0, num_methods):
                method_2 = methods[id_2]
                if not method_2.discard():
                    edge_label = method_1.get_edge_label(method_2)
                    if edge_label != "":
                        new_adj_list.append((id_2, edge_label))
        method_1.set_adj_list(new_adj_list)
    # discard methods that are dominated by themselves with a different configuration
    undiscarded_method_ids = []
    for id_1 in range(0, num_methods):
        method_1 = methods[id_1]
        new_adj_list = []
        if not method_1.discard():
            undiscarded_method_ids.append(id_1)
            old_adj_list = method_1.get_adj_list()
            for edge in old_adj_list:
                if not methods[edge[0]].discard():
                    new_adj_list.append(edge)
        method_1.set_adj_list(new_adj_list)
    # compute transitive reduction of undiscarded methods
    is_discarded_edge = {id_1 : {id_2 : False for id_2 in undiscarded_method_ids} for id_1 in undiscarded_method_ids}
    for method_id in undiscarded_method_ids:
        method = methods[method_id]
        seen = {child_id : False for child_id in undiscarded_method_ids}
        for edge in method.get_adj_list():
            dfs(methods, is_discarded_edge, method_id, edge[0], seen)
    # discard edges that are not contained in transitive reduction
    for id_1 in range(0, num_methods):
        method_1 = methods[id_1]
        new_adj_list = []
        if not method_1.discard():
            old_adj_list = method_1.get_adj_list()
            for edge in old_adj_list:
                if not is_discarded_edge[id_1][edge[0]]:
                    new_adj_list.append(edge)
        method_1.set_adj_list(new_adj_list)
    # compute scores    
    best_dist = 0
    best_t = 0
    best_coeff = 0
    for method in methods:
        if method.discard():
            continue
        if method.has_tightest_dist():
            best_dist = method.dist()
        if method.is_fastest():
            best_t = method.t
        if method.has_best_coeff():
            best_coeff = method.coeff()
    for method in methods:
        method.set_score(best_dist, best_t, best_coeff)
    return methods

def infix(args):
    the_infix = ""
    if args.lsape:
        the_infix = the_infix + "_lsape"
    if args.ls:
        the_infix = the_infix + "_ls"
    if args.lp:
        the_infix = the_infix + "_lp"
    if args.misc:
        the_infix = the_infix + "_misc"
    return the_infix

class AggregatedScores:
    
    def __init__(self, method_names, scores_lb, scores_ub, multi_sol_score, centralities_score, multi_start_score, randpost_score):
        self.method_names = method_names
        self.scores_lb = scores_lb
        self.scores_ub = scores_ub
        self.multi_sol_score = multi_sol_score
        self.centralities_score = centralities_score
        self.multi_start_score = multi_start_score
        self.ranpost_score = randpost_score
    
    def write_to_csv_file(self, args):
        csv_file_name = os.path.join(args.table_dir, args.dataset) + infix(args) + ".csv"
        csv_file = open(csv_file_name, "w")
        csv_file.write("heuristic;score_lb;score_ub\n")
        for method_name in self.method_names:
            csv_file.write(method_name + ";")
            if computes_no_lb(method_name):
                csv_file.write("na;")
            else:
                csv_file.write(str(self.scores_lb[method_name]) + ";")
            if computes_no_ub(method_name):
                csv_file.write("na\n")
            else:
                csv_file.write(str(self.scores_ub[method_name]) + "\n")
        csv_file.write("MULTISOL;na;" + str(self.multi_sol_score) + "\n")
        csv_file.write("CENTRALITIES;na;" + str(self.centralities_score) + "\n")
        csv_file.write("MULTISTART;na;" + str(self.multi_start_score) + "\n")
        csv_file.write("RANDPOST;na;" + str(self.ranpost_score) + "\n")
        csv_file.close()
                
def aggregate_scores(methods):
    method_names = set()
    for method in methods:
        method_names.add(method.name)
    scores_lb = {method_name : 0.0 for method_name in method_names}
    scores_ub = {method_name : 0.0 for method_name in method_names}
    sum_scores_ub_lsape = 0.0
    sum_scores_ub_centralities = 0.0
    sum_scores_ub_multi_sol = 0.0
    sum_scores_ub_ls = 0.0
    sum_scores_ub_randpost = 0.0
    sum_scores_ub_multi_start = 0.0
    for method in methods:
        if method.is_maximum_lb:
            if method.score_lb > scores_lb[method.name]:
                scores_lb[method.name] = method.score_lb
        if method.is_maximum_ub:
            if method.score_ub > scores_ub[method.name]:
                scores_ub[method.name] = method.score_ub
            if is_lsape_based(method):
                sum_scores_ub_lsape = sum_scores_ub_lsape + method.score_ub
            if uses_centralities(method):
                sum_scores_ub_centralities = sum_scores_ub_centralities + method.score_ub
            if uses_multi_sol(method):
                sum_scores_ub_multi_sol = sum_scores_ub_multi_sol + method.score_ub
            if is_ls_based(method):
                sum_scores_ub_ls = sum_scores_ub_ls + method.score_ub
            if uses_multi_start(method):
                sum_scores_ub_multi_start = sum_scores_ub_multi_start + method.score_ub
            if uses_randpost(method):
                sum_scores_ub_randpost = sum_scores_ub_randpost + method.score_ub
    multi_sol_score = 0
    centralities_score = 0
    multi_start_score = 0
    randpost_score = 0
    if sum_scores_ub_lsape > 0:
        multi_sol_score = sum_scores_ub_multi_sol / sum_scores_ub_lsape
        centralities_score = sum_scores_ub_centralities / sum_scores_ub_lsape
    if sum_scores_ub_ls > 0:
        multi_start_score = sum_scores_ub_multi_start / sum_scores_ub_ls
        randpost_score = sum_scores_ub_randpost / sum_scores_ub_ls
    return AggregatedScores(method_names, scores_lb, scores_ub, multi_sol_score, centralities_score, multi_start_score, randpost_score)
                

def create_table(args, methods):
    table_file_name = os.path.join(args.table_dir, args.dataset) + infix(args) + ".tex"
    # write csv file containing only maxima
    table_file = open(table_file_name, "w")
    table_file.write("%!TEX root = ../root.tex\n")
    table_file.write("\\begin{tabular}{llSSSS[table-format=1.2]S[table-format=1.2]S[table-format=1.2]S[table-format=1.2]}\n")
    table_file.write("\\toprule\n")
    table_file.write("heuristic & configuration & {$d_{\LB}$} & {$d_{\UB}$} & {$t$} & {$c_{\LB}$} & {$c_{\UB}$} & {$s_{\LB}$} & {$s_{\UB}$} \\\\\n")
    table_file.write("\midrule\n")
    for method in methods:
        table_file.write(method.as_table_row())
    table_file.write("\\bottomrule\n")
    table_file.write("\end{tabular}")
    table_file.close()
    

def create_tikz_file(args, methods, consider_lb):
    tikz_file_name = os.path.join(args.tikz_dir, args.dataset) + infix(args)
    if consider_lb:
        tikz_file_name = tikz_file_name + "_LB.tex"
    else:
        tikz_file_name = tikz_file_name + "_UB.tex"
    # construct tikz file
    tikz_file = open(tikz_file_name, "w")
    tikz_file.write("%!TEX root = ../root.tex\n")
    tikz_file.write("\input{img/tikzstyles}\n")
    tikz_file.write("\\begin{tikzpicture}[rounded corners]\n")
    tikz_file.write("\graph[layered layout,\n")
    tikz_file.write("level distance=15mm,\n")
    tikz_file.write("nodes={minimum width=4mm, minimum height=4mm, align=center, font=\scriptsize},\n")
    tikz_file.write("edge quotes mid,\n")
    tikz_file.write("edges={nodes={font=\scriptsize, fill=white, inner sep=1.5pt}}] {\n")
    edge_id = 0
    tikz_file.write("{ [same layer]\n")
    for method_id in range(0, len(methods)):
        method = methods[method_id]
        if (not method.discard()) and method.is_maximum():
            tikz_file.write(str(method_id) + " [" + method.name + ", as={" + method.tikz_descriptor() + "}, label=above:{\\footnotesize " + method.label() + "}],\n");
    tikz_file.write("};\n")
    for method_id in range(0, len(methods)):
        method = methods[method_id]
        if (not method.discard()) and (not method.is_maximum()):
            tikz_file.write(str(method_id) + " [" + method.name + ", as={" + method.tikz_descriptor() + "}];\n");
    for method_id in range(0, len(methods)):
        for edge in methods[method_id].get_adj_list():
            tikz_file.write(str(method_id) + " -> [" + edge[1] + "] " + str(edge[0]) + ";\n")
    tikz_file.write("};\n")
    tikz_file.write("\end{tikzpicture}")
    tikz_file.close()
    
    
parser = argparse.ArgumentParser(description="Generates TikZ dominance graph from CSV file.")
parser.add_argument("dataset", help="name of dataset")
parser.add_argument("tikz_dir", help="name of output directory for TikZ files")
parser.add_argument("table_dir", help="name of output directory for table")
parser.add_argument("--lsape", help="consider LSAPE based methods", action="store_true")
parser.add_argument("--ls", help="consider local search based methods", action="store_true")
parser.add_argument("--lp", help="consider LP based methods", action="store_true")
parser.add_argument("--misc", help="consider miscellaneous methods", action="store_true")

args = parser.parse_args()
methods = read_results_from_csv_files(args)
for consider_lb in [True, False]:
    methods = build_dependency_graph(methods, consider_lb)
    create_tikz_file(args, methods, consider_lb)
create_table(args, methods)
aggregated_scores = aggregate_scores(methods)
aggregated_scores.write_to_csv_file(args)