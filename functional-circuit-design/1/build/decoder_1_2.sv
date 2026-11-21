module decoder_testbench;
	reg sel1, sel2;
	wire [1:0] d1, d2;
	parameter N = 8;
	reg [$clog2(N)-1:0] sel3;
	wire [N-1:0] d3;
	reg clk, rst, en;
	
	decoder_1_assign first_decoder(sel1, d1);
	decoder_1_always second_decoder(sel2, d2);
	decoder_tree #(.N(N)) third_decoder(en, sel3, d3);
	result_keeper #(.N(N)) keeper_element(clk, rst, d3);
	
	initial begin
		// first decoder
		sel1 = 1'b0;
		#1;
		$display("first: expected 1 - found %0d", d1);
		sel1 = 1'b1;
		#1;
		$display("first: expected 2 - found %0d", d1);
	end
	
	initial begin
		// second decoder
		sel2 = 1'b0;
		#1;
		$display("second: expected 1 - found %0d", d2);
		sel2 = 1'b1;
		#1;
		$display("second: expected 2 - found %0d", d2);
	end
	
	initial begin
		// third decoder
		en = 1;
		for (int i = 0; i < N; i++) begin
			sel3 = i;
			#1;
			$display("third: expected %0d - found %0d", 1 << i, d3);
		end
	end
	
	initial begin
		// init keeper element
		$display("keeper: initial value - %0d", keeper_element.result);
		clk = 0;
		rst = 1;
		forever #5 clk = ~clk;
	end
	
	initial begin
		// test keeper
		for (int i = 1; i <= 8; i++) begin
			if (i == 3) begin
				$display("setting rst");
				rst = 0;
			end
			if (i == 6) begin
				$display("unsetting rst");
				rst = 1;
			end
			#6;
			$display("keeper: saved value #%0d - %0d", i, keeper_element.result);
		end
	end
endmodule

module decoder_1_assign
(
	input wire q,
	output wire [1:0] d
);
	assign d = (q == 1'b0) ? 2'b01 : 2'b10;
endmodule

module decoder_1_always
(
	input wire q,
	output reg [1:0] d
);	
	always @(*) begin
		if (q == 1'b0)
			d = 2'b01;
		else
			d = 2'b10;
	end
endmodule

module decoder_2_tuned
(
	input wire q, enable,
	output reg [1:0] d
);
	wire [1:0] decoder_d;
	decoder_1_assign decoder_1_to_2(q, decoder_d);
	assign d = ~enable ? 2'b00 : decoder_d;
endmodule

module decoder_tree
#(
	parameter int N = 2
)
(
	input wire enable,
	input wire [$clog2(N)-1:0] q,
	output wire [N-1:0] d
);
	generate
		if (N == 2) begin : g_leaf
			decoder_2_tuned u (
				.q(q[0]),
				.enable(enable),
				.d(d)
			);
		end else begin : g_node
			int MSB = $clog2(N) - 1;
			
			decoder_tree #(.N(N/2)) u_lo (
				.enable(enable & ~q[MSB]),
				.q(q[MSB-1:0]),
				.d(d[N/2-1:0])
			);
			decoder_tree #(.N(N/2)) u_hi (
				.enable(enable & q[MSB]),
				.q(q[MSB-1:0]),
				.d(d[N-1:N/2])
			);
		end
	endgenerate
endmodule

module result_keeper
#(
	parameter int N = 2
)
(
	input wire clk, rst,
	input wire [N-1:0] q
);
	reg [N-1:0] result = 0;
	always @(posedge clk) begin
		if (~rst)
			result <= 0;
		else
			result <= q;
	end
endmodule