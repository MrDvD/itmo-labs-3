module main
(
	input wire clk, start, done,
	input shortint a, b,
	output shortint c
);
	wire sum_start, sum_done;
	shortint sum_a, sum_b, sum_c;
	wire sum_done1, sum_done2, sum_done3;
	wire sum_start1, sum_start2, sum_start3;
	shortint sum_a1, sum_a2, sum_a3;
	shortint sum_b1, sum_b2, sum_b3;
	
	int mul_c;
	shortint mul_a, mul_b;
	wire mul_start, mul_done;
	
	wire sqrt_start, sqrt_done;
	wire cbrt_start, cbrt_done;
	
	shortint sqrt_x, sqrt_y;
	shortint cbrt_x, cbrt_y;
	
	summator sum_instance(
		.clk(clk),
		.start(sum_start),
		.done(sum_done),
		.a(sum_a), .b(sum_b),
		.c(sum_c)
	);
	multiplier mul_instance(
		.clk(clk),
		.start(mul_start),
		.done(mul_done),
		.a(mul_a), .b(mul_b),
		.c(mul_c)
	);
	
	square_root sqrt_instance(
		.clk(clk),
		.start(sqrt_start),
		.done(sqrt_done),
		.x(sqrt_x), .y(sqrt_y),
		
		.start_sub(sum_start1),
		.done_sub(sum_done1),
		.x_sub_arg(sum_a1), .b_sub_arg(sum_b1),
		.x_sub_res(sum_c)
	);
	cubic_root cbrt_instance(
		.clk(clk),
		.start(cbrt_start),
		.done(cbrt_done),
		.x(cbrt_x), .y(cbrt_y),
		
		.start_sub(sum_start2),
		.done_sub(sum_done2),
		.x_sub_arg(sum_a2), .b_sub_arg(sum_b2),
		.x_sub_res(sum_c),
		
		.start_mul(mul_start),
		.done_mul(mul_done),
		.a_mul_arg(mul_a), .b_mul_arg(mul_b),
		.c_mul_res(mul_c)
	);
	function_result fn_instance(
		.clk(clk),
		.start(start),
		.done(done),
		.a(a), .b(b),
		.c(c),
		
		.start_add(sum_start3),
		.done_add(sum_done3),
		.a_add_arg(sum_a3), .b_add_arg(sum_b3),
		.c_add_res(sum_c),
		
		.start_sqrt(sqrt_start),
		.done_sqrt(sqrt_done),
		.x_sqrt_arg(sqrt_x),
		.y_sqrt_res(sqrt_y),
		
		.start_cbrt(cbrt_start),
		.done_cbrt(cbrt_done),
		.x_cbrt_arg(cbrt_x),
		.y_cbrt_res(cbrt_y)
	);
	
	summator_controller ctrl_instance(
		.clk(clk),
		.a1(sum_a1), .b1(sum_b1),
		.a2(sum_a2), .b2(sum_b2),
		.a3(sum_a3), .b3(sum_b3),
		.start1(sum_start1), .start2(sum_start2), .start3(sum_start3),
		.sum_done(sum_done),
		
		.a(sum_a), .b(sum_b),
		.start(sum_start),
		.done1(sum_done1), .done2(sum_done2), .done3(sum_done3)
	);
endmodule

module sum_module_testbench;
	bit clk, start, done;
	shortint a, b, c;
	shortint idx;
	
	shortint test_data [3][10] = '{
		'{16'sd2, 16'sd0, 16'sd8, 16'sd0, 16'sd32767, 16'sd32767, -16'sd32768, 16'sd100, -16'sd1, 16'sd12345},
		'{16'sd2, 16'sd6, 16'sd9, 16'sd0, 16'sd1, -16'sd32768, -16'sd32768, -16'sd100, 16'sd1, 16'sd20000},
		'{16'sd4, 16'sd6, 16'sd17, 16'sd0, -16'sd32768, -16'sd1, 16'sd0, 16'sd0, 16'sd0, 16'sd32345}
	};
	
	initial begin
		idx = -1;
		#5
		idx = 0;
	end
	
	always #10 clk = ~clk;
	
	always @(idx) begin
		if (idx < 10) begin
			start = 1;
			a = test_data[0][idx];
			b = test_data[1][idx];
		end
	end
	
	always @(posedge done) begin
		$display("[sum_module_testbench] #%0d: expected %0d, actual %0d", idx, test_data[2][idx], c);
		idx += 1;
		start = 0;
	end

	summator sum_instance(
		.clk(clk),
		.start(start),
		.done(done),
		.a(a), .b(b),
		.c(c)
	);
endmodule

module multiply_module_testbench;
	bit clk, start, done;
	shortint a, b;
	shortint idx;
	int c;
	
	shortint test_args [2][3] = '{
		'{16'sd2, 16'sd0, 16'sd8},
		'{16'sd2, 16'sd6, 16'sd9}
	};
	
	int test_outs [3] = '{16'sd4, 16'sd0, 16'sd72};
	
	initial begin
		idx = -1;
		#5
		idx = 0;
	end
	
	always #10 clk = ~clk;
	
	always @(idx) begin
		if (idx < 3) begin
			start = 1;
			a = test_args[0][idx];
			b = test_args[1][idx];
		end
	end
	
	always @(posedge done) begin
		$display("[multiply_module_testbench] #%0d: expected %0d, actual %0d", idx, test_outs[idx], c);
		idx += 1;
		start = 0;
	end

	square_root sqrt_instance(
		.clk(clk),
		.start(start),
		.done(done),
		.a(a), .b(b),
		.c(c)
	);
endmodule

module sqrt_module_testbench;
	bit clk, start, done;
	shortint x, y;
	
	bit start_sub, done_sub;
	shortint a_sub, b_sub, c_sub;
	shortint idx;
	
	shortint test_data [2][10] = '{
    '{16'd0, 16'd1, 16'd2, 16'd3, 16'd4, 16'd9, 16'd15, 16'd16, 16'd25, 16'd65535},
    '{16'd0, 16'd1, 16'd1, 16'd1, 16'd2, 16'd3, 16'd3, 16'd4, 16'd5, 16'd255}
};
	
	initial begin
		idx = -1;
		#5
		idx = 0;
	end
	
	always #10 clk = ~clk;
	
	always @(idx) begin
		if (idx < 10) begin
			start = 1;
			x = test_data[0][idx];
		end
	end
	
	always @(posedge done) begin
		$display("[sqrt_module_testbench] #%0d: expected %0d, actual %0d", idx, test_data[1][idx], y);
		idx += 1;
		start = 0;
	end

	square_root sqrt_instance(
		.clk(clk),
		.start(start),
		.done(done),
		.x(x), .y(y),
		
		.start_sub(start_sub), .done_sub(done_sub),
		.x_sub_arg(a_sub), .b_sub_arg(b_sub),
		.x_sub_res(c_sub)
	);
	
	summator sum_instance(
		.clk(clk),
		.start(start_sub),
		.done(done_sub),
		.a(a_sub), .b(b_sub),
		.c(c_sub)
	);
endmodule

module cbrt_module_testbench;
	bit clk, start, done;
	shortint x, y;
	
	bit start_sub, done_sub;
	bit start_mul, done_mul;
	shortint a_sub, b_sub, c_sub;
	shortint a_mul, b_mul;
	shortint idx;
	int c_mul;
	
	// shortint test_data [2][10] = '{
	//	'{16'd8, 16'd343, 16'd125, 16'd27, 16'd64, 16'd1, 16'd216, 16'd512, 16'd1000, 16'd1728},
	//	'{16'd2, 16'd7, 16'd5, 16'd3, 16'd4, 16'd1, 16'd6, 16'd8, 16'd10, 16'd12}
	//};
	shortint test_data [2][2] = '{
		'{16'd1000, 16'd216},
		'{16'd10, 16'd6}
	};
	
	initial begin
		idx = -1;
		#5
		idx = 0;
	end
	
	always #10 clk = ~clk;
	
	always @(idx) begin
		if (idx < 2) begin
			start = 1;
			x = test_data[0][idx];
		end
	end
	
	always @(posedge done) begin
		$display("[cbrt_module_testbench] #%0d: expected %0d, actual %0d", idx, test_data[1][idx], y);
		idx += 1;
		start = 0;
	end
	
	cubic_root cbrt_instance(
		.clk(clk),
		.start(start),
		.done(done),
		.x(x), .y(y),
		
		.start_sub(start_sub), .done_sub(done_sub),
		.x_sub_arg(a_sub), .b_sub_arg(b_sub),
		.x_sub_res(c_sub),
		
		.start_mul(start_mul), .done_mul(done_mul),
		.a_mul_arg(a_mul), .b_mul_arg(b_mul),
		.c_mul_res(c_mul)
	);
	
	summator sum_instance(
		.clk(clk),
		.start(start_sub),
		.done(done_sub),
		.a(a_sub), .b(b_sub),
		.c(c_sub)
	);
	
	multiplier mul_instance(
		.clk(clk),
		.start(start_mul),
		.done(done_mul),
		.a(a_mul), .b(b_mul),
		.c(c_mul)
	);
endmodule

module function_result_testbench;
	bit clk, start, done;
	shortint a, b, c;
	
	initial begin
		forever #10 clk = ~clk;
	end
	
	initial begin
		start = 1;
		a = 8;
		b = 9;
	end

	main test_main(
		.clk(clk), .start(start), .done(done),
		.a(a), .b(b), .c(c)
	);
endmodule

module summator
(
	input wire clk,
	input wire start,
	output bit done,
	input shortint a, b,
	output shortint c
);
	typedef enum bit [1:0] {
		IDLE,
		SUMMING
	} state_t;
	
	state_t state, state_next;
	
	always @(posedge clk) begin
		state <= state_next;
	end
	
	always @* begin
		state_next = state;
		
		done = 0;
		c = 0;
		
		case (state)
			IDLE: begin
				if (start) begin
					state_next = SUMMING;
				end
			end
			
			SUMMING: begin
				c = a + b;
				done = 1;
				state_next = IDLE;
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule

module multiplier
(
	input wire clk,
	input wire start,
	output bit done,
	input shortint a, b,
	output int c
);
	typedef enum bit [2:0] {
		IDLE,
		INIT_VARS,
		BRANCH_CTR,
		BRANCH_SUM,
		DO_SUM,
		INC_CTR,
		WRITE_RES
	} state_t;
	
	state_t state, state_next;
	int part_res, part_res_next;
	reg [3:0] ctr, ctr_next;
	
	always @(posedge clk) begin
		state <= state_next;
		ctr <= ctr_next;
		part_res <= part_res_next;
	end
	
	always @* begin
		state_next = state;
		ctr_next = ctr;
		part_res_next = part_res;
		
		done = 0;
		c = 0;
		
		case (state)
			IDLE: begin
				if (start) begin
					state_next = INIT_VARS;
				end
			end
			
			INIT_VARS: begin
				ctr_next = 0;
				part_res_next = 0;
				state_next = BRANCH_CTR;
			end
			
			BRANCH_CTR: begin
				if (ctr < 15) begin
					state_next = BRANCH_SUM;
				end else begin
					state_next = WRITE_RES;
				end
			end
			
			BRANCH_SUM: begin
				if (b[ctr] == 1'b1) begin
					state_next = DO_SUM;
				end else begin
					state_next = INC_CTR;
				end
			end
			
			DO_SUM: begin
				part_res_next += a << ctr;
				state_next = INC_CTR;
			end
			
			INC_CTR: begin
				ctr_next += 1'b1;
				state_next = BRANCH_CTR;
			end
			
			WRITE_RES: begin
				done = 1;
				c = part_res;
				state_next = IDLE;
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule

module square_root
(
	input wire clk,
	input wire start,
	output bit done,
	input shortint x,
	output shortint y,
	
	output bit start_sub,
	input wire done_sub,
	output shortint x_sub_arg,
	output shortint b_sub_arg,
	input shortint x_sub_res
);
	typedef enum bit [2:0] {
		IDLE,
		BRANCH_M,
		EXTRACT,
		BRANCH_X,
		SUB_BEGIN,
		SUB_WAIT,
		END_BRANCH,
		DONE
	} state_t;
	
	state_t state, state_next;
	shortint x_buf, x_buf_next;
	shortint y_buf, y_buf_next;
	shortint m, m_next;
	shortint b, b_neg;
	
	always @(posedge clk) begin
		state <= state_next;
		x_buf <= x_buf_next;
		y_buf <= y_buf_next;
		m <= m_next;
	end
	
	assign b = (y_buf << 1) | m;
	
	always @* begin
		state_next = state;
		x_buf_next = x_buf;
		y_buf_next = y_buf;
		m_next = m;
		
		done = 0;
		y = 0;
		start_sub = 0;
		x_sub_arg = x_buf;
		b_sub_arg = -b;
		
		case (state)
			IDLE: begin
				if (start) begin
					m_next = 16'b1 << 14;
					y_buf_next = 0;
					x_buf_next = x;
					state_next = BRANCH_M;
				end
			end
			
			BRANCH_M: begin
				if (m != 0) begin
					state_next = EXTRACT;
				end else begin
					state_next = DONE;
				end
			end
			
			EXTRACT: begin
				y_buf_next >>= 1;
				state_next = BRANCH_X;
			end
			
			BRANCH_X: begin
				if (x_buf >= b) begin
					state_next = SUB_BEGIN;
				end else begin
					state_next = END_BRANCH;
				end
			end
			
			SUB_BEGIN: begin
				start_sub = 1;
				state_next = SUB_WAIT;
			end
			
			SUB_WAIT: begin
				if (done_sub) begin
					x_buf_next = x_sub_res;
					y_buf_next |= m;
					state_next = END_BRANCH;
				end
			end
			
			END_BRANCH: begin
				m_next >>= 2;
				state_next = BRANCH_M;
			end
			
			DONE: begin
				y = y_buf;
				done = 1;
				state_next = IDLE;
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule

module cubic_root
(
	input wire clk,
	input wire start,
	output bit done,
	input shortint x,
	output shortint y,
	
	output bit start_sub,
	input wire done_sub,
	output shortint x_sub_arg, b_sub_arg,
	input shortint x_sub_res,
	
	output bit start_mul,
	input wire done_mul,
	output shortint a_mul_arg, b_mul_arg,
	input int c_mul_res
);
	typedef enum bit [3:0] {
		IDLE,
		BRANCH_S,
		SHIFT_Y,
		MUL_3_BEGIN,
		MUL_3_WAIT,
		MUL_SQ_BEGIN,
		MUL_SQ_WAIT,
		FINISH_B,
		BRANCH_X,
		SUB_BEGIN,
		SUB_WAIT,
		END_BRANCH,
		DONE
	} state_t;
	
	state_t state, state_next;
	bit signed [4:0] s, s_next;
	shortint x_buf, x_buf_next;
	shortint y_buf, y_buf_next;
	int b_buf, b_buf_next;
	bit is_sq, is_sq_next;
	
	always @(posedge clk) begin
		state <= state_next;
		x_buf <= x_buf_next;
		y_buf <= y_buf_next;
		b_buf <= b_buf_next;
		s <= s_next;
		is_sq <= is_sq_next;
	end
	
	always @* begin
		state_next = state;
		x_buf_next = x_buf;
		y_buf_next = y_buf;
		b_buf_next = b_buf;
		is_sq_next = is_sq;
		s_next = s;
		
		done = 0;
		y = 0;
		start_sub = 0;
		x_sub_arg = x_buf;
		b_sub_arg = shortint'(~b_buf + 1'b1);
		start_mul = 0;
		a_mul_arg = is_sq ? shortint'(b_buf) : 3;
		b_mul_arg = is_sq ? y_buf + 1'b1 : y_buf;
		
		case (state)
			IDLE: begin
				if (start) begin
					y_buf_next = 0;
					x_buf_next = x;
					s_next = 5'sd15;
					state_next = BRANCH_S;
				end
			end
			
			BRANCH_S: begin
				if (s > -3) begin
					state_next = SHIFT_Y;
				end else begin
					state_next = DONE;
				end
			end
			
			SHIFT_Y: begin
				y_buf_next <<= 1;
				state_next = MUL_3_BEGIN;
			end
			
			MUL_3_BEGIN: begin
				is_sq_next = 0;
				start_mul = 1;
				state_next = MUL_3_WAIT;
			end
			
			MUL_3_WAIT: begin
				if (done_mul) begin
					b_buf_next = c_mul_res;
					state_next = MUL_SQ_BEGIN;
				end
			end
			
			MUL_SQ_BEGIN: begin
				is_sq_next = 1;
				start_mul = 1;
				state_next = MUL_SQ_WAIT;
			end
			
			MUL_SQ_WAIT: begin
				if (done_mul) begin
					b_buf_next = c_mul_res;
					state_next = FINISH_B;
				end
			end
			
			FINISH_B: begin
				b_buf_next = (b_buf_next + 1'b1) << s;
				state_next = BRANCH_X;
			end
			
			BRANCH_X: begin
				if (x >= b_buf) begin
					state_next = SUB_BEGIN;
				end else begin
					state_next = END_BRANCH;
				end
			end
			
			SUB_BEGIN: begin
				start_sub = 1;
				state_next = SUB_WAIT;
			end
			
			SUB_WAIT: begin
				if (done_sub) begin
					x_buf_next = x_sub_res;
					y_buf_next += 1'b1;
					state_next = END_BRANCH;
				end
			end
			
			END_BRANCH: begin
				s_next -= 2'd3;
				state_next = BRANCH_S;
			end
			
			DONE: begin
				y = y_buf;
				done = 1;
				state_next = IDLE;
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule

module function_result
(
	input wire clk,
	input wire start,
	output bit done,
	input shortint a, b,
	output shortint c,
	
	output bit start_add,
	input wire done_add,
	output shortint a_add_arg, b_add_arg,
	input shortint c_add_res,
	
	output bit start_sqrt,
	input wire done_sqrt,
	output shortint x_sqrt_arg,
	input shortint y_sqrt_res,
	
	output bit start_cbrt,
	input wire done_cbrt,
	output shortint x_cbrt_arg,
	input shortint y_cbrt_res
);
	typedef enum bit [3:0] {
		IDLE,
		SQRT_BEGIN,
		SQRT_WAIT,
		CBRT_BEGIN,
		CBRT_WAIT,
		ADD_BEGIN,
		ADD_WAIT,
		DONE
	} state_t;
	
	state_t state, state_next;
	shortint a_buf, a_buf_next;
	shortint b_buf, b_buf_next;
	
	always @(posedge clk) begin
		state <= state_next;
		a_buf <= a_buf_next;
		b_buf <= b_buf_next;
	end
	
	always @* begin
		state_next = state;
		a_buf_next = a_buf;
		b_buf_next = b_buf;
		
		done = 0;
		c = 0;
		start_add = 0;
		a_add_arg = 0;
		b_add_arg = 0;
		start_sqrt = 0;
		x_sqrt_arg = 0;
		start_cbrt = 0;
		x_cbrt_arg = 0;
		
		case (state)
			IDLE: begin
				if (start) begin
					state_next = SQRT_BEGIN;
				end
			end
			
			SQRT_BEGIN: begin
				x_sqrt_arg = a;
				start_sqrt = 1;
				state_next = SQRT_WAIT;
			end
			
			SQRT_WAIT: begin
				if (done_sqrt) begin
					a_buf_next = a;
					state_next = CBRT_BEGIN;
				end
			end
			
			CBRT_BEGIN: begin
				x_cbrt_arg = b;
				start_cbrt = 1;
				state_next = CBRT_WAIT;
			end
			
			CBRT_WAIT: begin
				if (done_cbrt) begin
					b_buf_next = b;
					state_next = ADD_BEGIN;
				end
			end
			
			ADD_BEGIN: begin
				a_add_arg = a_buf;
				b_add_arg = b_buf;
				start_add = 1;
				state_next = ADD_WAIT;
			end
			
			ADD_WAIT: begin
				if (done_add) begin
					done = 1;
					c = c_add_res;
					state_next = IDLE;
				end
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule

module summator_controller
(
	input wire clk,
	
	input shortint a1, b1, a2, b2, a3, b3,
	input wire start1, start2, start3,
	input sum_done,
	
	output shortint a, b,
	output bit start,
	output bit done1, done2, done3
);
	typedef enum bit [2:0] {
		IDLE,
		SET_BUSY,
		WAIT,
		DONE
	} state_t;
	
	state_t state, state_next;
	reg [1:0] busy_num, next_busy_num;
	
	always @(posedge clk) begin
		busy_num <= next_busy_num;
		state <= state_next;
	end
	
	always @* begin
		next_busy_num = busy_num;
		state_next = state;
		start = 0;
		done1 = 0;
		done2 = 0;
		done3 = 0;
		a = 0;
		b = 0;
		
		case (state)
			IDLE: begin
				if (start1 | start2 | start3) begin
					state_next = SET_BUSY;
				end
			end
			
			SET_BUSY: begin
				if (start1) begin
					next_busy_num = 1;
					a = a1;
					b = b1;
					start = 1;
				end
				if (start2) begin
					next_busy_num = 1;
					a = a2;
					b = b2;
					start = 1;
				end
				if (start3) begin
					next_busy_num = 1;
					a = a3;
					b = b3;
					start = 1;
				end
				state_next = WAIT;
			end
			
			WAIT: begin
				if (sum_done) begin
					case (busy_num)
						1: done1 = 1;
						2: done2 = 1;
						3: done3 = 1;
						default: ;
					endcase
					next_busy_num = 0;
					state_next = IDLE;
				end
			end
			
			default: begin
				state_next = IDLE;
			end
		endcase
	end
endmodule