clf
%comparison
algData = tdfread("[weightedRandomComparison].txt");
randData = tdfread("[playScript05Comparison].txt");

figure(1)
hold on
plot(algData.Time/60,algData.Longest_Sequence)
plot(randData.Time/60,randData.Longest_Sequence)
hold off
xlabel("Time (min)")
ylabel("Max Splits")
ylim([0 600])
legend("Algorithm Max Splits", "Random Max Splits")
title("Weighting Algorithm vs. Random Algorithm")

figure(2)
hold on
plot(algData.Games,algData.Longest_Sequence)
plot(randData.Games,randData.Longest_Sequence)
hold off
xlim([0 100000])
xlabel("Games")
ylabel("Max Splits")
ylim([0 600])
legend("Algorithm Max Splits", "Random Max Splits")
title("Weighting Algorithm vs. Random Algorithm")

