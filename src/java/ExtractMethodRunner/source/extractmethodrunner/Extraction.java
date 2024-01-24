package extractmethodrunner;

import org.eclipse.ltk.core.refactoring.Change;

public interface Extraction extends Comparable<Extraction> {

	int start();
	
	int end();
	
	Change change();
	
	default boolean overlaps(Extraction e) {
		return !(end() < e.start() || start() > e.end());
	}

	@Override
	default int compareTo(Extraction o) {
		return start() != o.start()? o.start() - start(): end() - o.end();
	}
}
